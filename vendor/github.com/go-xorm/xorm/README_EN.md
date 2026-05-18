# xorm

[English](https://github.com/go-xorm/xorm/blob/master/README.md)

XORM is a simple and powerful ORM library for the Go language. It simplifies database operations.

[![CircleCI](https://circleci.com/gh/go-xorm/xorm.svg?style=shield)](https://circleci.com/gh/go-xorm/xorm) [![codecov](https://codecov.io/gh/go-xorm/xorm/branch/master/graph/badge.svg)](https://codecov.io/gh/go-xorm/xorm)
[![](https://goreportcard.com/badge/github.com/go-xorm/xorm)](https://goreportcard.com/report/github.com/go-xorm/xorm)
[![Join the chat at https://img.shields.io/discord/323460943201959939.svg](https://img.shields.io/discord/323460943201959939.svg)](https://discord.gg/HuR2CF3)

## Features

* Flexible mapping between structs and database tables, with automatic synchronization

* Transaction support

* Mixed raw SQL and ORM operations

* Chain-style API for simpler calls

* Function and struct conditions such as Id, In, Where, Limit, Join, Having, Table, Sql, and Cols

* Eager loading of structs

* Schema support (Postgres only)

* Caching support

* Automatic generation of XORM structs from the database

* Versioning (optimistic locking)

* Built-in SQL builder

* Context cache

## Drivers

The following Go database drivers and databases are supported:

* Mysql: [github.com/go-sql-driver/mysql](https://github.com/go-sql-driver/mysql)

* MyMysql: [github.com/ziutek/mymysql/godrv](https://github.com/ziutek/mymysql/godrv)

* Postgres: [github.com/lib/pq](https://github.com/lib/pq)

* Tidb: [github.com/pingcap/tidb](https://github.com/pingcap/tidb)

* SQLite: [github.com/mattn/go-sqlite3](https://github.com/mattn/go-sqlite3)

* MsSql: [github.com/denisenkom/go-mssqldb](https://github.com/denisenkom/go-mssqldb)

* MsSql: [github.com/lunny/godbc](https://github.com/lunny/godbc)

* Oracle: [github.com/mattn/go-oci8](https://github.com/mattn/go-oci8) (experimental support)

## Install

	go get github.com/go-xorm/xorm

## Documents

* [Operation Guide](http://xorm.io/docs)

* [GoWalker Code Document](http://gowalker.org/github.com/go-xorm/xorm)

* [Godoc Code Document](http://godoc.org/github.com/go-xorm/xorm)

# Quick Start

* Create an engine. The `driverName` and `dataSourceName` are the same as in the `database/sql` interface.

```Go
engine, err := xorm.NewEngine(driverName, dataSourceName)
```

* Define a struct that is synchronized with the table and automatically synchronize the struct to the database.

```Go
type User struct {
    Id int64
    Name string
    Salt string
    Age int
    Passwd string `xorm:"varchar(200)"`
    Created time.Time `xorm:"created"`
    Updated time.Time `xorm:"updated"`
}

err := engine.Sync2(new(User))
```

* Create an engine group.

```Go
dataSourceNameSlice := []string{masterDataSourceName, slave1DataSourceName, slave2DataSourceName}
engineGroup, err := xorm.NewEngineGroup(driverName, dataSourceNameSlice)
```

```Go
masterEngine, err := xorm.NewEngine(driverName, masterDataSourceName)
slave1Engine, err := xorm.NewEngine(driverName, slave1DataSourceName)
slave2Engine, err := xorm.NewEngine(driverName, slave2DataSourceName)
engineGroup, err := xorm.NewEngineGroup(masterEngine, []*Engine{slave1Engine, slave2Engine})
```

All `engine` fields can be replaced with `engineGroup`.

* The original `Query` also supports SQL statement query. The returned result type is `[]map[string][]byte`. `QueryString` returns `[]map[string]string`, and `QueryInterface` returns `[]map[string]interface{}`.

```Go
results, err := engine.Query("select * from user")
results, err := engine.Where("a = 1").Query()

results, err := engine.QueryString("select * from user")
results, err := engine.Where("a = 1").QueryString()

results, err := engine.QueryInterface("select * from user")
results, err := engine.Where("a = 1").QueryInterface()
```

* `Exec`: Execute an SQL statement.

```Go
affected, err := engine.Exec("update user set age = ? where name = ?", age, name)
```

* `Insert`: Insert one or more records.

```Go
affected, err := engine.Insert(&user)
// INSERT INTO struct () values ()

affected, err := engine.Insert(&user1, &user2)
// INSERT INTO struct1 () values ()
// INSERT INTO struct2 () values ()

affected, err := engine.Insert(&users)
// INSERT INTO struct () values (),(),()

affected, err := engine.Insert(&user1, &users)
// INSERT INTO struct1 () values ()
// INSERT INTO struct2 () values (),(),()
```

* `Get`: Query a single record.

```Go
has, err := engine.Get(&user)
// SELECT * FROM user LIMIT 1

has, err := engine.Where("name = ?", name).Desc("id").Get(&user)
// SELECT * FROM user WHERE name = ? ORDER BY id DESC LIMIT 1

var name string
has, err := engine.Table(&user).Where("id = ?", id).Cols("name").Get(&name)
// SELECT name FROM user WHERE id = ?

var id int64
has, err := engine.Table(&user).Where("name = ?", name).Cols("id").Get(&id)
has, err := engine.SQL("select id from user").Get(&id)
// SELECT id FROM user WHERE name = ?

var valuesMap = make(map[string]string)
has, err := engine.Table(&user).Where("id = ?", id).Get(&valuesMap)
// SELECT * FROM user WHERE id = ?

var valuesSlice = make([]interface{}, len(cols))
has, err := engine.Table(&user).Where("id = ?", id).Cols(cols...).Get(&valuesSlice)
// SELECT col1, col2, col3 FROM user WHERE id = ?
```

* `Exist`: Check whether a record exists.

```Go
has, err := testEngine.Exist(new(RecordExist))
// SELECT * FROM record_exist LIMIT 1

has, err = testEngine.Exist(&RecordExist{
		Name: "test1",
	})
// SELECT * FROM record_exist WHERE name = ? LIMIT 1

has, err = testEngine.Where("name = ?", "test1").Exist(&RecordExist{})
// SELECT * FROM record_exist WHERE name = ? LIMIT 1

has, err = testEngine.SQL("select * from record_exist where name = ?", "test1").Exist()
// select * from record_exist where name = ?

has, err = testEngine.Table("record_exist").Exist()
// SELECT * FROM record_exist LIMIT 1

has, err = testEngine.Table("record_exist").Where("name = ?", "test1").Exist()
// SELECT * FROM record_exist WHERE name = ? LIMIT 1
```

* `Find`: Query multiple records. You can use `Join` and `extends` together.

```Go
var users []User
err := engine.Where("name = ?", name).And("age > 10").Limit(10, 0).Find(&users)
// SELECT * FROM user WHERE name = ? AND age > 10 limit 10 offset 0

type Detail struct {
    Id int64
    UserId int64 `xorm:"index"`
}

type UserDetail struct {
    User `xorm:"extends"`
    Detail `xorm:"extends"`
}

var users []UserDetail
err := engine.Table("user").Select("user.*, detail.*")
    Join("INNER", "detail", "detail.user_id = user.id").
    Where("user.name = ?", name).Limit(10, 0).
    Find(&users)
// SELECT user.*, detail.* FROM user INNER JOIN detail WHERE user.name = ? limit 10 offset 0
```

* `Iterate` and `Rows`: Traverse the database based on conditions in either `Iterate` or `Rows` mode.

```Go
err := engine.Iterate(&User{Name:name}, func(idx int, bean interface{}) error {
    user := bean.(*User)
    return nil
})
// SELECT * FROM user

err := engine.BufferSize(100).Iterate(&User{Name:name}, func(idx int, bean interface{}) error {
    user := bean.(*User)
    return nil
})
// SELECT * FROM user Limit 0, 100
// SELECT * FROM user Limit 101, 100

rows, err := engine.Rows(&User{Name:name})
// SELECT * FROM user
defer rows.Close()
bean := new(Struct)
for rows.Next() {
    err = rows.Scan(bean)
}
```

* `Update`: Update data. Unless the `Cols` and `AllCols` functions are used, only non-null and non-zero fields are updated by default.

```Go
affected, err := engine.ID(1).Update(&user)
// UPDATE user SET ... Where id = ?

affected, err := engine.Update(&user, &User{Name:name})
// UPDATE user SET ... Where name = ?

var ids = []int64{1, 2, 3}
affected, err := engine.In(ids).Update(&user)
// UPDATE user SET ... Where id IN (?, ?, ?)

// force update indicated columns by Cols
affected, err := engine.ID(1).Cols("age").Update(&User{Name:name, Age: 12})
// UPDATE user SET age = ?, updated=? Where id = ?

// force NOT update indicated columns by Omit
affected, err := engine.ID(1).Omit("name").Update(&User{Name:name, Age: 12})
// UPDATE user SET age = ?, updated=? Where id = ?

affected, err := engine.ID(1).AllCols().Update(&user)
// UPDATE user SET name=?,age=?,salt=?,passwd=?,updated=? Where id = ?
```

* `Delete`: Deletes records. Note that at least one condition must be met for deletion. Otherwise, an error is reported. To clear the database, use `EmptyTable`.

```Go
affected, err := engine.Where(...).Delete(&user)
// DELETE FROM user Where ...

affected, err := engine.ID(2).Delete(&user)
// DELETE FROM user Where id = ?
```

* `Count`: Obtain the number of records.

```Go
counts, err := engine.Count(&user)
// SELECT count(*) AS total FROM user
```

* `Sum`: summation function.

```Go
agesFloat64, err := engine.Sum(&user, "age")
// SELECT sum(age) AS total FROM user

agesInt64, err := engine.SumInt(&user, "age")
// SELECT sum(age) AS total FROM user

sumFloat64Slice, err := engine.Sums(&user, "age", "score")
// SELECT sum(age), sum(score) FROM user

sumInt64Slice, err := engine.SumsInt(&user, "age", "score")
// SELECT sum(age), sum(score) FROM user
```

* Condition editor

```Go
err := engine.Where(builder.NotIn("a", 1, 2).And(builder.In("b", "c", "d", "e"))).Find(&users)
// SELECT id, name ... FROM user WHERE a NOT IN (?, ?) AND b IN (?, ?, ?)
```

* Multiple database operations in a single goroutine without using transactions

```Go
session := engine.NewSession()
defer session.Close()

user1 := Userinfo{Username: "xiaoxiao", Departname: "dev", Alias: "lunny", Created: time.Now()}
if _, err := session.Insert(&user1); err != nil {
    return err
}

user2 := Userinfo{Username: "yyy"}
if _, err := session.Where("id = ?", 2).Update(&user2); err != nil {
    return err
}

if _, err := session.Exec("delete from userinfo where username = ?", user2.Username); err != nil {
    return err
}

return nil
```

* Transactions within a single goroutine

```Go
session := engine.NewSession()
defer session.Close()

// add Begin() before any action
if err := session.Begin(); err != nil {
    // if returned then will rollback automatically
    return err
}

user1 := Userinfo{Username: "xiaoxiao", Departname: "dev", Alias: "lunny", Created: time.Now()}
if _, err := session.Insert(&user1); err != nil {
    return err
}

user2 := Userinfo{Username: "yyy"}
if _, err := session.Where("id = ?", 2).Update(&user2); err != nil {
    return err
}

if _, err := session.Exec("delete from userinfo where username = ?", user2.Username); err != nil {
    return err
}

// add Commit() after all actions
return session.Commit()
```

* Simplified transaction syntax

```Go
res, err := engine.Transaction(func(session *xorm.Session) (interface{}, error) {
    user1 := Userinfo{Username: "xiaoxiao", Departname: "dev", Alias: "lunny", Created: time.Now()}
    if _, err := session.Insert(&user1); err != nil {
        return nil, err
    }

    user2 := Userinfo{Username: "yyy"}
    if _, err := session.Where("id = ?", 2).Update(&user2); err != nil {
        return nil, err
    }

    if _, err := session.Exec("delete from userinfo where username = ?", user2.Username); err != nil {
        return nil, err
    }
    return nil, nil
})
```

* Context cache support: When enabled, single-object query results are cached and can be reused by subsequent queries.

```Go
	sess := engine.NewSession()
	defer sess.Close()

	var context = xorm.NewMemoryContextCache()

	var c2 ContextGetStruct
	has, err := sess.ID(1).ContextCache(context).Get(&c2)
	assert.NoError(t, err)
	assert.True(t, has)
	assert.EqualValues(t, 1, c2.Id)
	assert.EqualValues(t, "1", c2.Name)
	sql, args := sess.LastSQL()
	assert.True(t, len(sql) > 0)
	assert.True(t, len(args) > 0)

	var c3 ContextGetStruct
	has, err = sess.ID(1).ContextCache(context).Get(&c3)
	assert.NoError(t, err)
	assert.True(t, has)
	assert.EqualValues(t, 1, c3.Id)
	assert.EqualValues(t, "1", c3.Name)
	sql, args = sess.LastSQL()
	assert.True(t, len(sql) == 0)
	assert.True(t, len(args) == 0)
```

## Contributing

If you also want to contribute to xorm, see [CONTRIBUTING](https://github.com/go-xorm/xorm/blob/master/CONTRIBUTING.md). You can also join the QQ group for technical help and discussion.
Group 1: 280360085 (full)
Group 2: 795010183

## Credits

### Contributors

Thank you to all the contributors.[[Contribute](CONTRIBUTING.md)].
<a href="graphs/contributors"><img src="https://opencollective.com/xorm/contributors.svg?width=890&button=false" /></a>

### Backers

Thank you to all the backers. 🙏 [[Become a Backer](https://opencollective.com/xorm#backer)]

<a href="https://opencollective.com/xorm#backers" target="_blank"><img src="https://opencollective.com/xorm/backers.svg?width=890"></a>

### Sponsors

Become a sponsor to support xorm. Your logo will be displayed and linked to your website. [[Become a Sponsor](https://opencollective.com/xorm#sponsor)]

# Cases

* [Go](http://studygolang.com/) - [github.com/studygolang/studygolang](https://github.com/studygolang/studygolang)

* [Gitea](http://gitea.io) - [github.com/go-gitea/gitea](http://github.com/go-gitea/gitea)

* [Gogs](http://try.gogits.org) - [github.com/gogits/gogs](http://github.com/gogits/gogs)

* [grafana](https://grafana.com/) - [github.com/grafana/grafana](http://github.com/grafana/grafana)

* [github.com/m3ng9i/qreader](https://github.com/m3ng9i/qreader)

* [Wego](http://github.com/go-tango/wego)

* [Docker.cn](https://docker.cn/)

* [Xorm Adapter](https://github.com/casbin/xorm-adapter) for [Casbin](https://github.com/casbin/casbin) - [github.com/casbin/xorm-adapter](https://github.com/casbin/xorm-adapter)

* [Gowalker](http://gowalker.org) - [github.com/Unknwon/gowalker](http://github.com/Unknwon/gowalker)

* [Gobuild.io](http://gobuild.io) - [github.com/shxsun/gobuild](http://github.com/shxsun/gobuild)

* [Sudo China](http://sudochina.com) - [github.com/insionng/toropress](http://github.com/insionng/toropress)

* [Godaily](http://godaily.org) - [github.com/govc/godaily](http://github.com/govc/godaily)

* [YouGam](http://www.yougam.com/)

* [GoCMS - github.com/zzboy/GoCMS](https://github.com/zzdboy/GoCMS)

* [GoBBS - gobbs.domolo.com](http://gobbs.domolo.com/)

* [go-blog](http://wangcheng.me) - [github.com/easykoo/go-blog](https://github.com/easykoo/go-blog)

## Changelog

* **v0.7.0**
    * Fixed some bugs.

* **v0.6.6**
    * Fixed some bugs.

* **v0.6.5**
    * Introduced `engine.SetSchema` to support schemas. Currently, only Postgres is supported.
    * Added vgo support.
    * Added the `FindAndCount` function.
    * Introduced `NewEngineWithParams` to support special database parameters.
    * Fixed some bugs.

* **v0.6.4**
    * Added the capability of automatic read/write splitting.
    * Added the capability of using Query/QueryString/QueryInterface and Where/And together.
    * Added support for obtaining non-structural variables via `Get`.
    * Added `BufferSize` support by `Iterate`.
    * Fixed some bugs.

[More changelogs...](https://github.com/go-xorm/manual-zh-CN/tree/master/chapter-16)

## LICENSE

BSD License
[http://creativecommons.org/licenses/BSD/](http://creativecommons.org/licenses/BSD/)
