#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
YAML 字符串仓库 + FastAPI 接口（含 reset/type & reset_all）。
分类模型：type -> subtype -> name -> {"value": str, "meta": {...}}

运行依赖：
    pip install fastapi uvicorn pydantic pyyaml

启动：
    python string_repo_yaml.py --store ./strings.yaml --defaults ./defaults.yaml --host 0.0.0.0 --port 8000

API 路径前缀：/v1
"""

import argparse
import copy
import json
import os
import shutil
import tempfile
import threading
from typing import Any, Dict, List, Optional
import string, inspect

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn


# -----------------------------
# Pydantic 请求/响应模型
# -----------------------------
class StringItem(BaseModel):
    type: str = Field(..., description="一级类型，如 mysql/nginx/pgsql")
    subtype: str = Field(..., description="二级类型，如 fast/slow/normal")
    name: str = Field(..., description="条目名，如 extractor, analyzer, collector, recommender")
    value: str = Field(..., description="具体内容（提示词/模板/案例等, 当前只有提示词）")
    meta: Optional[Dict[str, Any]] = Field(default=None, description="可选元信息，如作者/版本/备注")

class ResetPayload(BaseModel):
    type: str = Field(..., description="要恢复的类型，如 mysql/nginx/pgsql")

# -----------------------------
# YAML 工具
# -----------------------------
def _yaml_load(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML 顶层应为 mapping：{path}")
    return data

def _yaml_dump_atomic(path: str, data: Dict[str, Any]) -> None:
    d = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp = tempfile.mkstemp(prefix=".strings.", suffix=".yaml", dir=d)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            data,
            f,
            allow_unicode=True,
            sort_keys=True,
            default_flow_style=False,
            indent=2,
        )
    shutil.move(tmp, path)  # 原子替换

# -----------------------------
# 仓库类（给后端内部直接用）
# -----------------------------
class StringRepository:
    """
        - defaults: 从 defaults.yaml 读入，视为“出厂配置”
        - store   : 工作库 strings.yaml，初次不存在时会用 defaults 全量初始化
        - reset(type)    : 将某个 type 的 store 覆盖为 defaults 中该 type
        - reset_all()    : 用 defaults 全量覆盖 store
        数据结构：data[type][subtype][name] = {"value": str, "meta": {...}}
    """

    def __init__(self, store_path: str, defaults_path: str, autosave: bool = True):
        self._store_path = store_path
        self._defaults_path = defaults_path
        self._autosave = autosave
        self._lock = threading.RLock()
        # 都从默认路径读，涉及到改的时候，就改 string yaml
        self._defaults: Dict[str, Any] = _yaml_load(self._defaults_path)
        self._data: Dict[str, Any] = _yaml_load(self._defaults_path)

        # 首次运行：若 store 为空，则用 defaults 初始化
        if (not self._data or len(self._data) == 0) and self._defaults:
            _yaml_dump_atomic(self._store_path, self._defaults)
            self._data = _yaml_load(self._store_path)

    # ----------- 内部工具 -----------
    def _save(self):
        if not self._autosave:
            return
        _yaml_dump_atomic(self._store_path, self._data)

    def _ensure_paths(self, type_: str, subtype: str) -> None:
        self._data.setdefault(type_, {}).setdefault(subtype, {})

    # ----------- 查询枚举 -----------
    def list_types(self) -> List[str]:
        with self._lock:
            return sorted(self._data.keys())

    def list_subtypes(self, type_: str) -> List[str]:
        with self._lock:
            if type_ not in self._data:
                return []
            return sorted(self._data[type_].keys())

    def list_names(self, type_: str, subtype: str) -> List[str]:
        with self._lock:
            if type_ not in self._data or subtype not in self._data[type_]:
                return []
            return sorted(self._data[type_][subtype].keys())

    def get(self, type_: str, subtype: str, name: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return (
                self._data.get(type_, {})
                .get(subtype, {})
                .get(name, None)
            )

    def get_mode(self, type_: str) -> str:
        """
            get model, fast slow, normal etc
        """
        with self._lock:
            mode = self._data.get(type_).get('mode', "slow")
            if mode not in ["fast", "slow", "normal"]:
                return "slow"
            else:
                return mode

    # ----------- 增删改 -----------
    def create(self, item: StringItem) -> None:
        with self._lock:
            self._ensure_paths(item.type, item.subtype)
            if item.name in self._data[item.type][item.subtype]:
                raise ValueError("条目已存在（type/subtype/name 重复）")
            self._data[item.type][item.subtype][item.name] = {
                "value": item.value,
                "meta": item.meta,
            }
            self._save()

    def upsert(self, item: StringItem) -> None:
        with self._lock:
            self._ensure_paths(item.type, item.subtype)
            self._data[item.type][item.subtype][item.name] = {
                "value": item.value,
                "meta": item.meta,
            }
            self._save()

    def delete(self, type_: str, subtype: str, name: str) -> bool:
        with self._lock:
            if (
                type_ in self._data
                and subtype in self._data[type_]
                and name in self._data[type_][subtype]
            ):
                del self._data[type_][subtype][name]
                # 清理空层级
                if not self._data[type_][subtype]:
                    del self._data[type_][subtype]
                if type_ in self._data and not self._data[type_]:
                    del self._data[type_]
                self._save()
                return True
            return False

    # ----------- 恢复能力 -----------
    def reset_type(self, type_: str) -> None:
        with self._lock:
            if type_ not in self._defaults:
                raise ValueError(f"defaults.yaml 中不存在类型：{type_}")
            # 用 defaults[type] 覆盖到 store[type]
            self._data[type_] = copy.deepcopy(self._defaults[type_])
            self._save()

    def reset_all(self) -> None:
        with self._lock:
            if not self._defaults:
                raise ValueError("defaults.yaml 为空，无法执行 reset_all")
            self._data = copy.deepcopy(self._defaults)
            self._save()
    
    @staticmethod
    def render_by_parse(tpl: str, allowed: set, default: str = "未知"):
        """
            tpl: 模板字符串，含 {field[:fmt][!conv]}
            allowed: 允许替换的字段全集（如 {'self.service_name','self.performance_metric.name',...}）
            default: 不在 allowed 或取值失败时的占位
            返回: (渲染后字符串, 额外占位符列表)
        """
        fmt = string.Formatter()
        f = inspect.currentframe().f_back
        # 记录上一个调用栈的所有变量信息
        scope = {**f.f_globals, **f.f_locals}

        def resolve(field: str):
            parts = field.split('.')
            cur = scope.get(parts[0], None)
            for p in parts[1:]:
                if cur is None: return None
                cur = (cur.get(p) if isinstance(cur, dict) else getattr(cur, p, None))
            return cur

        out, extras = [], []
        for literal, field, format_spec, conversion in fmt.parse(tpl):
            out.append(literal)
            if not field:
                continue
            # 需要的变量不再提供的可用变量里面，直接改值为 “未知”，同时记录这个额外的 “需求变量”
            if field not in allowed:
                out.append(default)
                extras.append(field)
                continue
            val = resolve(field)
            if val is None:
                out.append(default)
                extras.append(field)
                continue
            # 格式化/转换
            try:
                val = format(val, format_spec) if format_spec else str(val)
            except Exception:
                val = str(val)
            if conversion == 'r':
                val = repr(val)
            elif conversion == 'a':
                val = ascii(val)
            out.append(str(val))
        # extras 去重保序
        seen, uniq = set(), []
        for e in extras:
            if e not in seen:
                seen.add(e)
                uniq.append(e)
        return ''.join(out), uniq


# ----------------------------------------------------------
# FastAPI（对前端/其他服务）
# ----------------------------------------------------------
def build_app(repo: StringRepository) -> FastAPI:
    app = FastAPI(title="String Repository (YAML)", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产可收敛到具体前端域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    prefix = "/v1"

    @app.get(prefix + "/types", response_model=List[str], summary="列出所有类型")
    def list_types():
        return repo.list_types()

    @app.get(prefix + "/subtypes/{type}", response_model=List[str], summary="列出某类型的所有子类型")
    def list_subtypes(type: str):
        subs = repo.list_subtypes(type)
        if not subs:
            raise HTTPException(status_code=404, detail="类型不存在或无子类型")
        return subs

    @app.get(prefix + "/names/{type}/{subtype}", response_model=List[str], summary="列出条目名称")
    def list_names(type: str, subtype: str):
        names = repo.list_names(type, subtype)
        if not names:
            raise HTTPException(status_code=404, detail="类型/子类型不存在或无条目")
        return names

    @app.get(prefix + "/strings/{type}/{subtype}/{name}", summary="获取具体条目")
    def get_string(type: str, subtype: str, name: str):
        item = repo.get(type, subtype, name)
        if not item:
            raise HTTPException(status_code=404, detail="未找到该条目")
        return {"type": type, "subtype": subtype, "name": name, **item}

    @app.post(prefix + "/strings", status_code=201, summary="新增（重复会 409）")
    def create_string(item: StringItem):
        try:
            repo.create(item)
            return {"ok": True}
        except ValueError as e:
            raise HTTPException(status_code=409, detail=str(e))

    @app.put(prefix + "/strings", summary="新增或更新（幂等 Upsert）")
    def upsert_string(item: StringItem):
        repo.upsert(item)
        return {"ok": True}

    @app.delete(prefix + "/strings/{type}/{subtype}/{name}", summary="删除一个条目")
    def delete_string(type: str, subtype: str, name: str):
        ok = repo.delete(type, subtype, name)
        if not ok:
            raise HTTPException(status_code=404, detail="删除失败：条目不存在")
        return {"ok": True}

    @app.post(prefix + "/reset/type", summary="恢复指定类型为 defaults.yaml 中的出厂配置")
    def reset_type(payload: ResetPayload):
        try:
            repo.reset_type(payload.type)
            return {"ok": True, "reset": payload.type}
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @app.post(prefix + "/reset/all", summary="恢复所有类型为 defaults.yaml 的出厂配置")
    def reset_all():
        try:
            repo.reset_all()
            return {"ok": True, "reset": "all"}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    return app


# ----------------------------------------------------------
# CLI & 启动
# ----------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser(description="YAML 字符串仓库服务")
    p.add_argument("--store", type=str, default="./config/strings.yaml", help="工作库 YAML 路径")
    p.add_argument("--defaults", type=str, default="./config/defaults.yaml", help="出厂默认 YAML 路径")
    p.add_argument("--host", type=str, default="127.0.0.1")
    p.add_argument("--port", type=int, default=8000)
    return p.parse_args()


def main():
    args = parse_args()
    repo = StringRepository(store_path=args.store, defaults_path=args.defaults, autosave=True)
    app = build_app(repo)
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    print("app start ...")
    main()
