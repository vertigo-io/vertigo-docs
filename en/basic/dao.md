# DAO

In Vertigo projects, data access is implemented in DAO objects and relies on the use of Store and Tasks.

## Store

In DAO objects generated during MDA, data access methods are offered. They allow the following operations from a Java API:

- creation
- selection by primary key
- update
- deletion
- selection by search criteria (use of the [Criteria](#criteria) API)
- manipulation of N-N type relationships

These methods allow direct storage manipulation from a Java API and are therefore easily usable by a developer. They cover a large portion of storage interactions with very little effort.

Here is an example of using the selection by primary key method:

```java
@Override
public Movie getMovieById(final Long movId) {
	Assertion.checkNotNull(movId);
	// ---
	return movieDAO.get(movId);
}
```


?> The methods offered are limited to manipulating a single business entity because this guarantees good performance. Since performance control is essential for an operational system, we recommend using the store for simple cases and using a dedicated [Task](#tasks) for more complex cases, especially when multiple entities are involved.

!> It is important to always favor set-based data operations (selection and modification) and avoid multiple unitary calls, which have a significant and uncontrolled performance cost.


## Criteria

The API offers the following features by providing search types:

- Null/Not null
- Equals/Not equals
- StartsWith
- GreaterThan/GreaterThanOrEqual/LowerThan/LowerThanOrEqual
- Between
- In

Additionally, it allows fluid chaining of *and* and *or* clauses.

A "criteria" is built as follows:

```java
final Criteria<Movie> criteria = Criterions.startsWith(MovieFields.name, title)
					  .and(Criterions.isEqualTo(MovieFields.year, year));
```

and is used directly from a DAO object:

```java
movieDAO.findAll(criteria, 500);
```


## Tasks

When database operations are more complex, it is preferable to use a query native to the storage system. Tasks allow performing these operations.

A Task abstracts the concept of data manipulation regardless of the underlying technical element. It is defined by:

- a name
- an execution engine: `className`
- a query: providing the processing to be performed
- input parameters
- an optional output parameter

A Task is created by declaring it in a KSP file.

### Execution Engine

Vertigo includes a number of execution engines. Given the nature of applications built with Vertigo, these engines are designed for SQL query execution. Here are the main ones:

- `io.vertigo.basics.task.TaskEngineSelect`: allows data selection from a relational database in SQL (*select* type query)
- `io.vertigo.basics.task.TaskEngineProc`: allows data manipulation in a relational database in SQL (*update* and *delete* type queries)
- `io.vertigo.basics.task.TaskEngineProcBatch`: allows batch type queries with an input parameter of type `DtList`


### Parameters

Task parameters are defined by:

- whether it is an input or output parameter
- a name: usable in the query as a bound parameter
- a domain: specifies its type (in the Vertigo sense). For objects, the following *domain* exists: Do*Object*
- the cardinality associated with the parameter (`1`, `?` or `*`)

### Query

The query is a text field containing the processing to be performed.

This field allows the use of input parameters as bound parameters using the following syntax:

- *#primitiveParameterName#*: for a primitive parameter
- *#primitiveParameterName.rownum#*: for a primitive list type parameter and field usage in batch type queries

- *#objectParameter.field#*: for an object type parameter and field usage
- *#objectListParameter.index.field#*: for an object list type parameter and field usage (*to use for clauses of type Where IN(...)*)
- *#listParameter.field#*: for a list type parameter and field usage in batch type queries

Additionally, it is also possible to add dynamism to queries by using the `<%><%>` syntax, which allows inserting Java code that will be interpreted at execution time. This is notably used to activate or deactivate parts of queries.

```
 create Task TkGetMoviesByCriteria {
    className : "io.vertigo.basics.task.TaskEngineSelect"
        request : "
        	select mov.*
        	from movie mov
        	where
        	1=1
        	<%if(title != null) {%>
	         and mov.NAME like concat(#title#, '%%')
        	<%}%>
        	<%if(year != null) {%>
	         and mov.YEAR = #year#
        	<%}%>
			"
	in title	 	{domain : DoLabelLong 		cardinality:"1" 	}
	in year	 		{domain : DoYear 			cardinality:"1" 	}
	out movies		{domain : DoDtMovie	 		cardinality:"*" 	}
}
```


For more details on using these syntaxes, a complete [workshop](/guide/samples_dao) is available.

### Escaping Example

To escape a character like `"`, you can use `\`

Example commonly used for passing the security clause:

`where ass.usr_Id = #usrId# and <%=securedAssignement.asSqlWhere(\"ass\", ctx)%>`


### Example of TaskEngineSelect
Here is an example of a Task declaration that retrieves a list of actors who participated in a film.

```
create Task TkGetActorsInMovie {
    className : "io.vertigo.basics.task.TaskEngineSelect"
        request : "
        	select act.*
        	from role rol
        	join actor act on act.ACT_ID = rol.ACT_ID
        	where rol.MOV_ID = #movId#
			"
	in 	movId		{domain : DoId 				cardinality:"1" 	}
	out actors		{domain : DoDtActor 		cardinality:"*"		}
}

```
Once this Task is declared and the generator executed, a new method is available in the associated DAO. Tasks are placed in the DAO of the object concerned by the parameters (output or input) when there is no ambiguity, or in a PAO (Package Access Object) otherwise.

```java
public io.vertigo.dynamo.domain.model.DtList<io.vertigo.samples.dao.domain.Actor> getActorsInMovie(final Long movId) {
		final Task task = createTaskBuilder("TkGetActorsInMovie")
				.addValue("movId", movId)
				.build();
		return getTaskManager()
				.execute(task)
				.getResult();
}
```
This task can then be called very simply by a business service through this DAO.

```java
@Override
public DtList<Actor> getActorsByMovie2(final Long movId) {
	return actorDAO.getActorsInMovie(movId);
}
```

### Example of TaskEngineProcBatch

With a TaskEngine of type TaskEngineProcBatch, it is possible to apply the fields of list elements line by line to perform set-based updates.

Like this:
```
create Task TkUpdateActorsNameBatch {
    className : "io.vertigo.basics.task.TaskEngineProcBatch"
        request : "
        	UPDATE actor
        	SET name = #actors.name#
            WHERE act_id = #actors.actId#;
			"
	in actors		{domain : DoDtActor 		cardinality:"*"		}
    out intSqlRowcount  {domain : DoNumber      cardinality: "1" }
}
```

This example is fictional; in many cases it is simpler to use the entity's DAO and its `updateList(final DtList<E> entities)` method.
