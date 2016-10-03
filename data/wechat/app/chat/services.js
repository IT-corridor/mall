angular.module('chat.services', ['ngResource'])
    .constant('chat_path', 'visitor/chat/')
    .factory('Chat', ['$resource', 'chat_path', 'API',
        function($resource, chat_path, API) {
            return $resource(API + chat_path + ':pk/:action/', {}, {
                create_session: {
                    method: 'POST',
                    params: {
                        action: 'create_session'
                    },
                    responseType: 'json'
                },
                destroy_session: {
                    method: 'POST',
                    params: {
                        action: 'destroy_session'
                    },
                    responseType: 'json'
                },

            });
        }
    ])
    .factory('Quickblox', ['$rootScope', '$window', '$q', 'Chat',
        function($rootScope, $window, $q, Chat) {
            var defer = $q.defer();
            var promise = defer.promise;

            var defer_chat = $q.defer();
            var promise_chat = defer_chat.promise;

            var roster = {};
            var Quickblox = {};
            var users = {};
            var contacts = [];
            var CONFIG = {
                debug: {
                    mode: 1
                }
            };
            $rootScope.messages = [];
            var user_storage = {
                current_page: 1,
                items: []
            };
            var subscribers = [];
            $rootScope.credentials = Chat.create_session(function(success) {

                QB.init(success.token, success.app_id);
                defer.resolve();
            });

            Quickblox.connect = function() {
                promise.then(function(success) {

                    QB.chat.connect({
                        userId: $rootScope.credentials.qid,
                        password: $rootScope.credentials.password
                    }, function(err, roster) {

                        if (err) {
                            defer_chat.reject(err);
                        } else {
                            defer_chat.resolve(roster);
                            var ids = Object.keys(roster);
                            var filter = {field: 'id', param: 'in', value: ids};
                            var promise_u = users.get_list(null, null, filter);
                            promise_u.then(function(success){
                                var i = 0, l = success.length;
                                for (i; i < l; i++){
                                    contacts.push(success[i]);
                                }
                            },
                            function(err){
                                console.log(err);
                            }
                            );

                        }
                    });
                    QB.chat.onDisconnectedListener = onDisconnectedListener;
                    QB.chat.onMessageListener = onMessage;
                    QB.chat.onSubscribeListener = onSubscribe;
                    QB.chat.onConfirmSubscribeListener = onConfirmSubscribe;
                    QB.chat.onRejectSubscribeListener = onRejectSubscribe;
                    QB.chat.onContactListListener = onContactList;
                });
            };

            Quickblox.get_dialogs = function(params) {
                var inner = $q.defer();
                promise.then(function(success) {
                    var filters = params;

                    QB.chat.dialog.list(filters, function(err, res) {
                        if (err) {
                            inner.reject(err);
                        } else {
                            inner.resolve(res);
                        }
                    });

                });
                return inner.promise;
            };

            Quickblox.create_private = function(occupant_id) {
                var inner = $q.defer();
                promise.then(function(success) {
                    var params = {
                        type: 3,
                        occupants_ids: [occupant_id],
                    };

                    QB.chat.dialog.create(params, function(err, res) {
                        if (err) {
                            inner.reject(err);
                        } else {
                            inner.resolve(res);
                        }
                    });

                });
                return inner.promise;
            };

            Quickblox.delete_dialog = function(dialog_ids) {
                /* dialog_ids Array expected */
                var inner = $q.defer();
                promise.then(function(success) {
                    QB.chat.dialog.delete(dialog_ids, function(err) {
                        if (err) {
                            inner.reject(err);
                        } else {
                            inner.resolve(res);
                        }
                    });

                });
                return inner.promise;
            };

            Quickblox.send_message = function(opponent_id, body) {
                var inner = $q.defer();
                promise.then(function(success) {
                    var msg = {
                        type: 'chat',
                        body: body,
                        extension: {
                            save_to_history: 1,
                        }
                    };
                    QB.chat.send(opponentId, msg);
                    inner.resolve();
                });
                return inner.promise;
            };

            Quickblox.unread_count = function(dialog_ids) {
                /* dialog_ids Array expected */
                var params = {
                    chat_dialog_ids: dialog_ids
                };
                var inner = $q.defer();
                promise.then(function(success) {
                    QB.chat.message.unreadCount(params, function(err, res) {
                        if (err) {
                            inner.reject(err);
                        } else {
                            inner.resolve(res);
                        }
                    });

                });
                return inner.promise;
            };

            Quickblox.message_list = function(dialog_id) {
                var params = {
                    chat_dialog_id: dialog_id,
                    sort_desc: 'date_sent',
                    limit: 100,
                    skip: 0
                };
                var inner = $q.defer();

                promise.then(function(success) {
                    QB.chat.message.list(params, function(err, res) {
                        if (err) {
                            inner.reject(err);
                        } else {
                            inner.resolve(res);
                        }
                    });

                });

                return inner.promise;
            };

            /*USERS*/

            Quickblox.get_users = function(filter) {
                console.log('here');
                // TODO: make it easy
                var inner = $q.defer();
                if (!user_storage.total_entries || user_storage.items.length < user_storage.total_entries) {
                    var params = {
                        page: user_storage.current_page,
                        per_page: '10',
                        filter: filter,
                    };

                    promise.then(function(success) {
                        QB.users.listUsers(params, function(err, res) {
                            if (err) {
                                inner.reject(err);
                            } else {
                                user_storage.current_page += 1;
                                user_storage.total_entries = res.total_entries;
                                user_storage.items = user_storage.items.concat(res.items);
                                inner.resolve(user_storage.items);
                            }
                        });

                    });
                } else {
                    inner.reject('error');
                }
                return inner.promise;
            };

            users.get_list = function(page, per_page, filter) {
                var inner = $q.defer();

                var params = {
                    page: page,
                    per_page: per_page,
                    filter: filter,
                };

                promise.then(function(success) {
                    QB.users.listUsers(params, function(err, res) {
                        if (err) {
                            inner.reject(err);
                        } else {
                            inner.resolve(res.items);
                        }
                    });

                });

                return inner.promise;
            };

             users.get = function(user_id) {
                var inner = $q.defer();

                promise.then(function(success) {
                    QB.users.get(user_id, function(err, res) {
                        if (err) {
                            inner.repromiject(err);
                        } else {
                            inner.resolve(res);
                        }
                    });

                });
                return inner.promise;
            };


            /* ROSTER */

            roster.get = function() {
                var inner = $q.defer();

                promise_chat.then(function(success) {
                    QB.chat.roster.get(function(res) {
                        console.log(res);
                        inner.resolve(res);
                    });
                });

                return inner.promise;
            };

            roster.add_user = function(jidOrUserId) {
                var inner = $q.defer();

                promise_chat.then(function(success) {
                    QB.chat.roster.add(jidOrUserId, function() {
                        var p = users.get(jidOrUserId);
                        p.then(function (success){
                            contacts.push({'user': success});
                        });
                       inner.resolve();

                       console.log(contacts);
                    });

                });

                return inner.promise;
            };

            roster.remove = function(jidOrUserId) {
                var inner = $q.defer();

                promise_chat.then(function(success) {
                    QB.chat.roster.remove(jidOrUserId, function() {

                    });

                });

                return inner.promise;
            };

            roster.confirm = function(jidOrUserId) {
                var inner = $q.defer();

                promise_chat.then(function(success) {
                    QB.chat.roster.confirm(jidOrUserId, function() {
                        // TODO
                    });

                });

                return inner.promise;
            };

            roster.reject = function(jidOrUserId) {
                var inner = $q.defer();

                promise_chat.then(function(success) {
                    QB.chat.roster.reject(jidOrUserId, function() {
                        // TODO
                    });

                });

                return inner.promise;
            };


            roster.confirm_user = function(user){
                var promise = roster.confirm(user.id);
                promise.then(function(success){
                    var index = subscribers.indexOf(user);
                    console.log(index);
                    subscribers.splice(index, 1);
                });

            };

            roster.remove_user = function(user){
                console.log('here');
                var inner = roster.remove(user.id);
                inner.then(function(success){
                    var index = contacts.indexOf(user);
                    console.log(index);
                    contacts.splice(index, 1);
                });
            }

            roster.get_users = function(){
                var roster_promise = roster.get();
                roster_promise.then(function(success){
                    var ids = Object.keys(success);
                    var filter = {field: 'id', param: 'in', value: ids};
                    var promise_u = users.get_list(null, null, filter);
                    promise_u.then(function(success){
                        console.log(success);
                    },
                    function(err){
                        console.log(err);
                    }
                    );
                    contacts.push(success);
                    console.log(success);
                });
            };


            Quickblox.disconnect = function() {
                QB.chat.disconnect();
            };

            function onDisconnectedListener() {
                Chat.destroy_session({
                    'token': $rootScope.credentials.token
                });
            }

            function onMessage(user_id, msg) {
                if (typeof $rootScope.messages[user_id] === 'undefined') {
                    $rootScope.messages[user_id] = Array();
                }
                // set dialog_id instead of
                $rootScope.messages[user_id].push(msg);

            };

            function onSubscribe(userId) {
                var promise = users.get(userId);
                promise.then(function(success){
                    console.log(success);
                    subscribers.push({'id': success.id, 'full_name': success.full_name});
                });
            };

            function onConfirmSubscribe(userId) {
                // ToDO
            };

            function onRejectSubscribe(userId) {
                // ToDO
            };

            function onContactList(userId, type) {
                // ToDO
            };

            Quickblox.subscribers = subscribers;
            Quickblox.contacts = contacts;
            Quickblox.users = users;
            Quickblox.roster = roster;
            return Quickblox;
        }
    ]);
