# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"
__author__ = 'maxaon'
import redis as aaa
from bson import SON, ObjectId
import pymongo.database
from pymongo.collection import Collection

class Redis(aaa.Redis):
    pass


class Database(pymongo.database.Database):
    '''
    MongoDatabase with some sugar
    '''

    def __init__(self, connection, name):
        super(Database, self).__init__(connection, name)

    def collection(self, name):
        return self.__getattr__(name)


class BaseCollection(Collection):
    '''
    Mongo collection with sugar:
    BaseCollection._db - default database
    _name - name of the collection
    _primary - primary key of the collection. Type is dictionary. Format: {'key_name': <type>,'key_name2':<type>}
        types:
            1 - simple value
            "$oid" ObjectID
    _model - model for the collectio. Type = `ActiveRecord` (maybe `SON`)

    '''
    _db = None
    _name = None
    _primary = {"_id": "$oid"}
    _model = None

    def __init__(self, database=None, name=None, model=None, create=False, **kwargs):
        """Get / create a Mongo collection.

       Raises :class:`TypeError` if `name` is not an instance of
       :class:`basestring` (:class:`str` in python 3). Raises
       :class:`~pymongo.errors.InvalidName` if `name` is not a valid
       collection name. Any additional keyword arguments will be used
       as options passed to the create command. See
       :meth:`~pymongo.database.Database.create_collection` for valid
       options.

       If `create` is ``True`` or additional keyword arguments are
       present a create command will be sent. Otherwise, a create
       command will not be sent and the collection will be created
       implicitly on first use.

       :Parameters:
         - `database`: the database to get a collection from. If ``None`` default database is used
         - `name`: the name of the collection to get. If ``None`` name will be used from static field
         - `model`:`ActiveRecord` Model of the data witch will be used for data representation
         - `create` (optional): if ``True``, force collection
           creation even without options being set
         - `**kwargs` (optional): additional keyword arguments will
           be passed as options for the create collection command

       .. versionchanged:: 2.2
          Removed deprecated argument: options

       .. versionadded:: 2.1
          uuid_subtype attribute

       .. versionchanged:: 1.5
          deprecating `options` in favor of kwargs

       .. versionadded:: 1.5
          the `create` parameter

       .. mongodoc:: collections
       """
        if not database:
            database = self.db
        if name: self._name = name or self._name
        if model: self._model = model
        if self._model:
            #set collection to model for short path
            self._model._collection = self
        if not self._name:
            raise ValueError("Name of collection doesnt supplied")
        super(BaseCollection, self).__init__(database, self._name, create, **kwargs)

    def find_by_primary(self, data):
        '''
        '''
        #We have simple case
        if len(self._primary) == 1:
            if isinstance(data, dict):
                raise ValueError("Key contain one value. More values are passed")
            key, value = self._primary.keys()[0], self._primary.values()[0]
            if isinstance(value, str) and value == '$oid':
                data = ObjectId(data)
            return self.find_one({key: data})
        else:
            raise NotImplementedError("Multivalue keys not implemented")


    def find(self, *args, **kwargs):
        """Query the database.

        The `spec` argument is a prototype document that all results
        must match. For example:

        >>> db.test.find({"hello": "world"})

        only matches documents that have a key "hello" with value
        "world".  Matches can have other keys *in addition* to
        "hello". The `fields` argument is used to specify a subset of
        fields that should be included in the result documents. By
        limiting results to a certain subset of fields you can cut
        down on network traffic and decoding time.

        Raises :class:`TypeError` if any of the arguments are of
        improper type. Returns an instance of
        :class:`~pymongo.cursor.Cursor` corresponding to this query.

        :Parameters:
          - `spec` (optional): a SON object specifying elements which
            must be present for a document to be included in the
            result set
          - `fields` (optional): a list of field names that should be
            returned in the result set or a dict specifying the fields
            to include or exclude. If `fields` is a list "_id" will
            always be returned. Use a dict to exclude fields from
            the result (e.g. fields={'_id': False}).
          - `skip` (optional): the number of documents to omit (from
            the start of the result set) when returning the results
          - `limit` (optional): the maximum number of results to
            return
          - `timeout` (optional): if True, any returned cursor will be
            subject to the normal timeout behavior of the mongod
            process. Otherwise, the returned cursor will never timeout
            at the server. Care should be taken to ensure that cursors
            with timeout turned off are properly closed.
          - `snapshot` (optional): if True, snapshot mode will be used
            for this query. Snapshot mode assures no duplicates are
            returned, or objects missed, which were present at both
            the start and end of the query's execution. For details,
            see the `snapshot documentation
            <http://dochub.mongodb.org/core/snapshot>`_.
          - `tailable` (optional): the result of this find call will
            be a tailable cursor - tailable cursors aren't closed when
            the last data is retrieved but are kept open and the
            cursors location marks the final document's position. if
            more data is received iteration of the cursor will
            continue from the last document received. For details, see
            the `tailable cursor documentation
            <http://www.mongodb.org/display/DOCS/Tailable+Cursors>`_.
          - `sort` (optional): a list of (key, direction) pairs
            specifying the sort order for this query. See
            :meth:`~pymongo.cursor.Cursor.sort` for details.
          - `max_scan` (optional): limit the number of documents
            examined when performing the query
          - `as_class` (optional): class to use for documents in the
            query result (default is taken from _model)
          - `slave_okay` (optional): if True, allows this query to
            be run against a replica secondary.
          - `await_data` (optional): if True, the server will block for
            some extra time before returning, waiting for more data to
            return. Ignored if `tailable` is False.
          - `partial` (optional): if True, mongos will return partial
            results if some shards are down instead of returning an error.
          - `manipulate`: (optional): If True (the default), apply any
            outgoing SON manipulators before returning.
          - `network_timeout` (optional): specify a timeout to use for
            this query, which will override the
            :class:`~pymongo.connection.Connection`-level default
          - `read_preference` (optional): The read preference for
            this query.
          - `tag_sets` (optional): The tag sets for this query.
          - `secondary_acceptable_latency_ms` (optional): Any replica-set
            member whose ping time is within secondary_acceptable_latency_ms of
            the nearest member may accept reads. Default 15 milliseconds.

        .. note:: The `manipulate` parameter may default to False in
           a future release.

        .. note:: The `max_scan` parameter requires server
           version **>= 1.5.1**

        .. versionadded:: 2.3
           The `tag_sets` and `secondary_acceptable_latency_ms` parameters.

        .. versionadded:: 1.11+
           The `await_data`, `partial`, and `manipulate` parameters.

        .. versionadded:: 1.8
           The `network_timeout` parameter.

        .. versionadded:: 1.7
           The `sort`, `max_scan` and `as_class` parameters.

        .. versionchanged:: 1.7
           The `fields` parameter can now be a dict or any iterable in
           addition to a list.

        .. versionadded:: 1.1
           The `tailable` parameter.

        .. mongodoc:: find
        """

        if "as_class" not in kwargs: kwargs['as_class'] = self._model
        return super(BaseCollection, self).find(*args, **kwargs)


    def insert(self, doc_or_docs, manipulate=True, safe=None, check_keys=True, continue_on_error=False, **kwargs):
        """Insert a document(s) into this collection.

        Before manipulation `doc_or_docs` converted to `_model`

        If `manipulate` is ``True``, the document(s) are manipulated using
        any :class:`~pymongo.son_manipulator.SONManipulator` instances
        that have been added to this :class:`~pymongo.database.Database`.
        In this case an ``"_id"`` will be added if the document(s) does
        not already contain one and the ``"id"`` (or list of ``"_id"``
        values for more than one document) will be returned.
        If `manipulate` is ``False`` and the document(s) does not include
        an ``"_id"`` one will be added by the server. The server
        does not return the ``"_id"`` it created so ``None`` is returned.

        Write concern options can be passed as keyword arguments, overriding
        any global defaults. Valid options include w=<int/string>,
        wtimeout=<int>, j=<bool>, or fsync=<bool>. See the parameter list below
        for a detailed explanation of these options.

        By default an acknowledgment is requested from the server that the
        insert was successful, raising :class:`~pymongo.errors.OperationFailure`
        if an error occurred. **Passing ``w=0`` disables write acknowledgement
        and all other write concern options.**

        :Parameters:
          - `doc_or_docs`: a document or list of documents to be
            inserted
          - `manipulate` (optional): If ``True`` manipulate the documents
            before inserting.
          - `safe` (optional): **DEPRECATED** - Use `w` instead.
          - `check_keys` (optional): If ``True`` check if keys start with '$'
            or contain '.', raising :class:`~pymongo.errors.InvalidName` in
            either case.
          - `continue_on_error` (optional): If ``True``, the database will not
            stop processing a bulk insert if one fails (e.g. due to duplicate
            IDs). This makes bulk insert behave similarly to a series of single
            inserts, except lastError will be set if any insert fails, not just
            the last one. If multiple errors occur, only the most recent will
            be reported by :meth:`~pymongo.database.Database.error`.
          - `w` (optional): (integer or string) If this is a replica set, write
            operations will block until they have been replicated to the
            specified number or tagged set of servers. `w=<int>` always includes
            the replica set primary (e.g. w=3 means write to the primary and wait
            until replicated to **two** secondaries). **Passing w=0 disables
            write acknowledgement and all other write concern options.**
          - `wtimeout` (optional): (integer) Used in conjunction with `w`.
            Specify a value in milliseconds to control how long to wait for
            write propagation to complete. If replication does not complete in
            the given timeframe, a timeout exception is raised.
          - `j` (optional): If ``True`` block until write operations have been
            committed to the journal. Ignored if the server is running without
            journaling.
          - `fsync` (optional): If ``True`` force the database to fsync all
            files before returning. When used with `j` the server awaits the
            next group commit before returning.
        :Returns:
          - The ``'_id'`` value (or list of '_id' values) of `doc_or_docs` or
            ``[None]`` if manipulate is ``False`` and the documents passed
            as `doc_or_docs` do not include an '_id' field.

        .. note:: `continue_on_error` requires server version **>= 1.9.1**

        .. versionadded:: 2.1
           Support for continue_on_error.
        .. versionadded:: 1.8
           Support for passing `getLastError` options as keyword
           arguments.
        .. versionchanged:: 1.1
           Bulk insert works with any iterable

        .. mongodoc:: insert
        """
        docs = doc_or_docs
        return_one = False
        if isinstance(docs, dict):
            return_one = True
            docs = [docs]

        docs = [doc if isinstance(doc, ActiveRecord) else self._model(doc) for doc in docs]

        ids = super(BaseCollection, self).insert(docs, manipulate, safe, check_keys, continue_on_error, **kwargs)

        return return_one and docs[0] or docs


    @property
    def db(self):
        if not getattr(BaseCollection, '_db'):
            raise ValueError("Base model doesn't have default adapter")
        return BaseCollection._db


class ActiveRecord(SON):
    '''

    Implement
    active
    record
    pattern
    for SON objects.
    '''
    _defaults = {}

    @property
    def collection(self):
        """
        @rtype: BaseCollection
        @return:
        """
        col = getattr(self, "_collection")
        if not isinstance(col, BaseCollection):
            if not col:
                raise ValueError("Collection not specified for class '{}'".format(self.__class__.__name__))
            setattr(self, "_collection", col())
        col = getattr(self, "_collection")
        return  col

    def __init__(self, data=None, **kwargs):
        if 'collection' in kwargs:
            self._collection = kwargs.pop('collection')
        super(ActiveRecord, self).__init__(data, **kwargs)


    def __getattr__(self, item):
        if item in self.keys():
            return self[item]
        elif item in self._defaults:
            return self._defaults[item]
        else:
            raise AttributeError


    def __setattr__(self, key, value):
        if not key.startswith("_"):
            self[key] = value
        super(ActiveRecord, self).__setattr__(key, value)

    def __repr__(self):
        result = []
        for key in self.keys():
            result.append("(%r, %r)" % (key, self[key]))
        return self.__class__.__name__ + "([%s])" % ", ".join(result)

    def save(self, manipulate=True, safe=None, check_keys=True, **kwargs):
        '''
        """Save current document in this collection.

       If `to_save` already has an ``"_id"`` then an :meth:`update`
       (upsert) operation is performed and any existing document with
       that ``"_id"`` is overwritten. Otherwise an :meth:`insert`
       operation is performed. In this case if `manipulate` is ``True``
       an ``"_id"`` will be added to `to_save` and this method returns
       the ``"_id"`` of the saved document. If `manipulate` is ``False``
       the ``"_id"`` will be added by the server but this method will
       return ``None``.

       Raises :class:`TypeError` if `to_save` is not an instance of
       :class:`dict`.

       Write concern options can be passed as keyword arguments, overriding
       any global defaults. Valid options include w=<int/string>,
       wtimeout=<int>, j=<bool>, or fsync=<bool>. See the parameter list below
       for a detailed explanation of these options.

       By default an acknowledgment is requested from the server that the
       save was successful, raising :class:`~pymongo.errors.OperationFailure`
       if an error occurred. **Passing ``w=0`` disables write acknowledgement
       and all other write concern options.**

       :Parameters:
         - `manipulate` (optional): manipulate the document before
           saving it?
         - `safe` (optional): **DEPRECATED** - Use `w` instead.
         - `check_keys` (optional): check if keys start with '$' or
           contain '.', raising :class:`~pymongo.errors.InvalidName`
           in either case.
         - `w` (optional): (integer or string) If this is a replica set, write
           operations will block until they have been replicated to the
           specified number or tagged set of servers. `w=<int>` always includes
           the replica set primary (e.g. w=3 means write to the primary and wait
           until replicated to **two** secondaries). **Passing w=0 disables
           write acknowledgement and all other write concern options.**
         - `wtimeout` (optional): (integer) Used in conjunction with `w`.
           Specify a value in milliseconds to control how long to wait for
           write propagation to complete. If replication does not complete in
           the given timeframe, a timeout exception is raised.
         - `j` (optional): If ``True`` block until write operations have been
           committed to the journal. Ignored if the server is running without
           journaling.
         - `fsync` (optional): If ``True`` force the database to fsync all
           files before returning. When used with `j` the server awaits the
           next group commit before returning.
       :Returns:
         - The ``'_id'`` value of `to_save` or ``[None]`` if `manipulate` is
           ``False`` and `to_save` has no '_id' field.

       .. versionadded:: 1.8
          Support for passing `getLastError` options as keyword
          arguments.

       .. mongodoc:: insert
       """

        :return:
        '''

        col = self.collection
        col.save(self, manipulate, safe, check_keys, **kwargs)

if __name__ == "__main__":
    pass