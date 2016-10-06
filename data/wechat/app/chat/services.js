angular.module('chat.services', ['ngResource'])
    .constant('chat_path', 'visitor/chat/')
    .factory('Chat', ['$resource', 'chat_path', 'API',
        function ($resource, chat_path, API) {
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
    .factory('Quickblox', ['$rootScope', '$q', 'Chat',
        function ($rootScope, $q, Chat) {
            // TODO: make it cleaner
            /*This is a Angularjs factory for Quickblox API */
            var d = $q.defer(), // global defer for object
                dc = $q.defer(), // global chat defer
                pc = dc.promise,
                p = d.promise
            self = null;

            var Quickblox = {
                init: function () {
                    // trick for storing self reference.
                    self = this;
                },
                credentials: Chat.create_session(function (success) {
                    QB.init(success.token, success.app_id);
                    d.resolve();
                }),
                connect: function () {
                    var self = this;
                    p.then(function (success) {
                        QB.chat.connect({
                            userId: self.credentials.qid,
                            password: self.credentials.password
                        }, function (err, res) {
                            /*roster expected as res*/
                            if (err) {
                                dc.reject(err);
                            } else {
                                dc.resolve(res);
                                var ids = Object.keys(res);
                                if (ids.length > 0) {
                                    var filter = {
                                        field: 'id',
                                        param: 'in',
                                        value: ids
                                    };
                                    // Works
                                    var p_contacts = self.users.get_list(null, null, filter);
                                    p_contacts.then(function (success) {
                                            self.contacts = success.items;
                                        },
                                        function (error) {
                                            console.log(error);
                                        }
                                    );
                                    var p_dialogs = self.dialogs.get_list(null);
                                    p_dialogs.then(function (success) {
                                        self.storage.dialogs = success.items;
                                        console.log(self.storage.dialogs);
                                    }, function (error) {
                                        console.log(error);
                                    });
                                }
                            }
                        });

                        QB.chat.onDisconnectedListener = self.on_disconnected;
                        QB.chat.onMessageListener = self.on_message;
                        QB.chat.onDeliveredStatusListener = self.on_delivered_status;
                        QB.chat.onSubscribeListener = self.on_subscribe;
                        QB.chat.onConfirmSubscribeListener = self.on_confirm_subscribe;
                        QB.chat.onRejectSubscribeListener = self.on_reject_subscribe;
                        QB.chat.onContactListListener = self.on_contact_list;

                    });
                },
                disconnect: function () {
                    QB.chat.disconnect();
                },
                dialogs: {
                    get_list: function (params) {
                        var inner = $q.defer();
                        p.then(function (success) {
                            QB.chat.dialog.list(params, function (err, res) {
                                if (err) {
                                    inner.reject(err);
                                } else {
                                    inner.resolve(res);
                                }
                            });
                        });
                        return inner.promise;
                    },
                    create_dialog: function (params) {
                        var inner = $q.defer();
                        p.then(function (success) {

                            QB.chat.dialog.create(params, function (err, res) {
                                if (err) {
                                    console.log(err);
                                    inner.reject(err);
                                } else {
                                    inner.resolve(res);
                                }
                            });

                        });
                        return inner.promise;
                    },
                    remove: function (dialog_ids) {
                        /* dialog_ids Array expected */
                        var inner = $q.defer();
                        p.then(function (success) {
                            QB.chat.dialog.delete(dialog_ids, function (err) {
                                if (err) {
                                    inner.reject(err);
                                } else {
                                    inner.resolve(res);
                                }
                            });

                        });
                        return inner.promise;
                    },
                    set_dialog: function (dialog) {
                        self.current_dialog = dialog;
                        self.messages.check_message_storage(dialog);
                    },
                    create_private: function (user_id) {
                        // Also fetches one if it is already created
                        var inner = $q.defer();
                        var params = {
                            type: 3,
                            occupants_ids: [user_id],
                        };
                        var promise_create = this.create_dialog(params);
                        promise_create.then(function (success) {
                            inner.resolve(success);
                            self.storage.dialogs.push(success);
                            console.log(success);
                        }, function (error) {
                            inner.reject(error);
                        });
                        return inner.promise;
                    }

                },
                messages: {
                    send: function (user_id, body) {
                        var inner = $q.defer();
                        p.then(function (success) {
                            var msg = {
                                type: 'chat',
                                body: body,
                                sender_id: self.credentials.qid,
                                date_sent: Math.round(new Date().getTime() / 1000),
                                extension: {
                                    save_to_history: 1,
                                },
                                //markable: 1
                            };
                            QB.chat.send(user_id, msg);
                            inner.resolve(msg);
                        });
                        return inner.promise;
                    },
                    send_occupants: function (dialog, body) {
                        /* Sending to all dialog occupants */
                        var inner = $q.defer();
                        p.then(function (success) {
                            var msg = {
                                type: 'chat',
                                body: body,
                                extension: {
                                    save_to_history: 1,
                                    sender_id: self.credentials.qid,
                                    date_sent: Math.round(new Date().getTime() / 1000),
                                    dialog_id: dialog._id
                                },
                                //markable: 1
                            };
                            var i = 0,
                                l = dialog.occupants_ids.length;
                            for (i; i < l; i++) {
                                QB.chat.send(dialog.occupants_ids[i], msg);
                            }

                            inner.resolve(msg);
                        });
                        return inner.promise;
                    },
                    unread_count: function (dialog_ids) {
                        /* dialog_ids Array expected */
                        var params = {
                            chat_dialog_ids: dialog_ids
                        };
                        var inner = $q.defer();
                        p.then(function (success) {
                            QB.chat.message.unreadCount(params, function (err, res) {
                                if (err) {
                                    inner.reject(err);
                                } else {
                                    inner.resolve(res);
                                }
                            });

                        });
                        return inner.promise;
                    },
                    get_list: function (params) {

                        var inner = $q.defer();

                        p.then(function (success) {
                            QB.chat.message.list(params, function (err, res) {
                                if (err) {
                                    inner.reject(err);
                                } else {
                                    inner.resolve(res);
                                }
                            });

                        });

                        return inner.promise;
                    },
                    get_list_by_user: function (user) {
                        var inner = $q.defer();
                        var params = {
                            sender_id: user.id,
                            sort_desc: 'date_sent',
                            limit: 100,
                            skip: 0
                        };
                        var promise_list = this.get_list(params);
                        promise_list.then(function (success) {
                            inner.resolve(success);
                        }, function (error) {
                            inner.reject(error);
                        });
                        return inner.promise;
                    },
                    get_list_by_dialog: function (dialog) {
                        var inner = $q.defer();
                        var params = {
                            chat_dialog_id: dialog._id,
                            sort_asc: 'date_sent',
                            limit: 100,
                            skip: 0
                        };
                        var promise_list = this.get_list(params);
                        promise_list.then(function (success) {
                            inner.resolve(success);
                        }, function (error) {
                            inner.reject(error);
                        });
                        return inner.promise;
                    },
                    check_message_storage: function (dialog) {
                        if (!self.storage.messages.hasOwnProperty(dialog._id)) {
                            self.storage.messages[dialog._id] = [];
                            var promise_list = self.messages.get_list_by_dialog(dialog);
                            promise_list.then(function (success) {
                                self.storage.messages[dialog._id] = self.storage.messages[dialog._id].concat(success.items);
                                //self.broadcast('ChatMessage');
                            });
                        }
                    },
                },
                users: {
                    get_list: function (page, per_page, filter) {
                        var inner = $q.defer();

                        var params = {
                            page: page,
                            per_page: per_page,
                            filter: filter,
                        };

                        p.then(function (success) {
                            QB.users.listUsers(params, function (err, res) {
                                if (err) {
                                    inner.reject(err);
                                } else {
                                    inner.resolve(res);
                                }
                            });

                        });

                        return inner.promise;
                    },
                    get: function (user_id) {
                        var inner = $q.defer();
                        p.then(function (success) {
                            QB.users.get(user_id, function (err, res) {
                                if (err) {
                                    inner.reject(err);
                                } else {
                                    inner.resolve(res);
                                }
                            });

                        });
                        return inner.promise;
                    },
                },
                roster: {
                    get: function () {
                        /* Get user`s roster*/
                        var inner = $q.defer();
                        pc.then(function (success) {
                            QB.chat.roster.get(function (res) {
                                console.log(res);
                                inner.resolve(res);
                            });
                        });
                        return inner.promise;
                    },
                    add: function (jidOrUserId) {
                        /* Subscribe on user*/
                        var inner = $q.defer();
                        pc.then(function (success) {
                            QB.chat.roster.add(jidOrUserId, function () {
                                inner.resolve();
                            });

                        });

                        return inner.promise;
                    },
                    remove: function (jidOrUserId) {
                        var inner = $q.defer();

                        pc.then(function (success) {
                            QB.chat.roster.remove(jidOrUserId, function () {
                                inner.resolve();
                            });

                        });
                        return inner.promise;
                    },
                    confirm: function (jidOrUserId) {
                        var inner = $q.defer();

                        pc.then(function (success) {
                            QB.chat.roster.confirm(jidOrUserId, function () {
                                // TODO
                                inner.resolve();
                            });

                        });

                        return inner.promise;
                        user
                    },
                    reject: function (jidOrUserId) {
                        var inner = $q.defer();
                        pc.then(function (success) {
                            QB.chat.roster.reject(jidOrUserId, function () {
                                // TODO
                                inner.resolve();
                            });

                        });
                        return inner.promise;
                    },


                },
                on_dictonnected: function () {
                    Chat.destroy_session({
                        'token': self.credentials.token
                    });
                },
                on_message: function (user_id, msg) {
                    console.log(user_id, msg);
                    msg['message'] = msg.body;
                    msg['sender_id'] = msg.extension.sender_id;
                    msg['date_sent'] = msg.extension.date_sent;

                    var check_arr = self.storage.dialogs.filter(function (element, index, arr) {
                        return element._id == msg.dialog_id;
                    });
                    if (check_arr.length == 0) {
                        var promise_create = self.dialogs.create_private(user_id);
                        promise_create.then(function (success) {
                            self.storage.messages[msg.dialog_id] = [];
                            self.storage.messages[msg.dialog_id].push(msg);
                        });
                    } else {

                        self.storage.messages[msg.dialog_id].push(msg);
                        console.log(msg);
                        self.broadcast('ChatMessage');
                    }
                },
                on_delivered_status: function (message_id, dialog_id, user_id) {
                    console.log(message_id, dialog_id, user_id);
                },
                on_subscribe: function (user_id) {
                    // Works
                    var promise_user = self.users.get(user_id);
                    promise_user.then(function (success) {
                        self.subscribers.push({
                            'id': success.id,
                            'full_name': success.full_name
                        });
                    });
                },
                on_confirm_subscribe: function (user_id) {
                    // TODO
                },
                on_reject_subscribe: function (user_id) {
                    // TODO
                },
                on_contact_list: function (user_id, type) {
                    // TODO
                    /*
                    Returns:
                      *  (Integer) userId - The sender ID
                      *  (String) type - If user leave the chat, type will be 'unavailable'
                    */
                },

                get_users: function (filter) {
                    // TODO: make it easy
                    // Works
                    var self = this;
                    var inner = $q.defer();
                    if (!self.user_storage.total_entries || self.user_storage.items.length < self.user_storage.total_entries) {
                        var page = self.user_storage.current_page,
                            per_page = 10,
                            filter = filter,
                            list_promise = self.users.get_list(page, per_page, filter);
                        list_promise.then(function (success) {
                            self.user_storage.current_page += 1;
                            self.user_storage.total_entries = success.total_entries;
                            self.user_storage.items = self.user_storage.items.concat(success.items);
                            inner.resolve(self.user_storage.items);
                        });
                    } else {
                        inner.reject('error');
                    }
                    return inner.promise;
                },
                confirm_user: function (user) {
                    var self = this;
                    var promise_confirm = self.roster.confirm(user.id);
                    promise_confirm.then(function (success) {
                        var index = self.subscribers.indexOf(user);
                        console.log(index);
                        self.subscribers.splice(index, 1);
                        // TODO: FIX;
                        //self.contacts.push(user);
                    });
                },
                unsubscribe_user: function (user) {
                    console.log('removing user');
                    var self = this;
                    var promise_remove = self.roster.remove(user.id);
                    promise_remove.then(function (success) {
                        var index = self.contacts.indexOf(user);
                        self.contacts.splice(index, 1);
                    });
                },
                subscribe_user: function (user) {
                    var self = this;
                    var promise_add = self.roster.add(user.id);
                    promise_add.then(function (success) {
                        var promise_user = self.users.get(user.id);
                        promise_user.then(function (success) {
                            self.contacts.push({
                                'user': success
                            });
                        });
                    });
                },
                get_contacts: function () {
                    /* First we query roster, then users*/
                    var self = this;
                    var roster_promise = self.roster.get();
                    roster_promise.then(function (success) {
                        var ids = Object.keys(success);
                        var filter = {
                            field: 'id',
                            param: 'in',
                            value: ids
                        };
                        var promise_u = self.users.get_list(null, null, filter);
                        promise_u.then(function (success) {
                                console.log(success);
                                self.contacts = self.contacts.concat(success);
                            },
                            function (err) {
                                console.log(err);
                            }
                        );
                        console.log(success);
                    });
                },
                set_opponent: function (user) {
                    self.opponent = user;
                    self.check_user_message_storage(user);
                },
                send_message: function (dialog, body) {
                    var p_send = self.messages.send_occupants(dialog, body);
                    p_send.then(function (success) {
                        // TODO
                    });
                },
                broadcast: function (signal) {
                    $rootScope.$broadcast(signal);
                },
                user_storage: {
                    current_page: 1,
                    items: []
                },
                contacts: [],
                subscribers: [],
                message_storage: {},
                opponent: null,
                current_dialog: null,
                opponent_storage: [],
                storage: {
                    dialogs: [],
                    messages: [],
                },

            };
            // DIRTY!!!
            Quickblox.init();

            return Quickblox;
        }
    ]);
