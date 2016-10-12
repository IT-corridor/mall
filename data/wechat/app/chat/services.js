angular.module('chat.services', ['ngResource', 'notification.services'])
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
                search: {
                    method: 'GET',
                    params: {
                        action: 'search',
                    },
                    responseType: 'json'
                },
                qid: {
                    method: 'GET',
                    params: {
                        action: 'qid'
                    },
                    responseType: 'json'
                },


            });
        }
    ])
    .service('Quickblox', ['$rootScope', '$q', '$log', 'Chat', 'Notification',
        function ($rootScope, $q, $log, Chat, Notification) {
            return function () {

                // TODO: make it cleaner
                /*This is a Angularjs factory for Quickblox API */
                var d = $q.defer(), // global defer for object
                    dc = $q.defer(), // global chat defer
                    pc = dc.promise,
                    p = d.promise,
                    self = null;

                var Quickblox = {
                    init: function () {
                        // trick for storing self reference.
                        self = this;
                    },
                    is_connected: false,
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
                                    var sorted_roster = self.roster.sort(res);
                                    self.users.perform_contacts(sorted_roster.contacts, 'contacts');
                                    self.users.perform_contacts(sorted_roster.i_subscribers, 'i_subscribers');
                                    self.users.perform_contacts(sorted_roster.o_subscribers, 'o_subscribers');
                                    var p_dialogs = self.dialogs.get_list(null);
                                    p_dialogs.then(function (success) {
                                        self.storage.dialogs = success.items;
                                    }, function (error) {
                                        console.log(error);
                                    });
                                    self.is_connected = true;
                                }
                            });

                            QB.chat.onDisconnectedListener = self.handlers.on_disconnected;
                            QB.chat.onMessageListener = self.handlers.on_message;
                            QB.chat.onDeliveredStatusListener = self.handlers.on_delivered_status;
                            QB.chat.onSubscribeListener = self.handlers.on_subscribe;
                            QB.chat.onConfirmSubscribeListener = self.handlers.on_confirm_subscribe;
                            QB.chat.onRejectSubscribeListener = self.handlers.on_reject_subscribe;
                            QB.chat.onContactListListener = self.handlers.on_contact_list;

                        });
                    },
                    disconnect: function () {
                        QB.chat.disconnect();
                        self.is_connected = false;
                        self.reset_storage();
                    },
                    reconnect: function () {
                        d = $q.defer();
                        dc = $q.defer();
                        pc = dc.promise;
                        p = d.promise;
                        self.credentials = Chat.create_session(function (success) {
                            QB.init(success.token, success.app_id);
                            d.resolve();
                        });
                        self.connect();
                    },
                    dialogs: {
                        get_list: function (params) {
                            /* Getting the dialogs list */
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
                            /* Creates a dialog. And (!) also fetches one if it is already created */
                            var inner = $q.defer();
                            var params = {
                                type: 3,
                                occupants_ids: [user_id],
                            };
                            var promise_create = this.create_dialog(params);
                            promise_create.then(function (success) {
                                inner.resolve(success);
                                self.storage.dialogs.push(success);
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
                            /* chat_dialog_id is required! */
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
                        perform_list: function (filter) {
                            // TODO: make it easy
                            // Works
                            var inner = $q.defer();
                            if (!self.storage.users.total_entries || self.storage.users.items.length < self.storage.users.total_entries) {
                                var page = self.storage.users.current_page,
                                    per_page = 10,
                                    filter = filter,
                                    list_promise = self.users.get_list(page, per_page, filter);
                                list_promise.then(function (success) {
                                    self.storage.users.current_page += 1;
                                    self.storage.users.total_entries = success.total_entries;
                                    self.storage.users.items = self.storage.users.items.concat(success.items);
                                    inner.resolve(self.storage.users.items);
                                });
                            } else {
                                inner.reject('error');
                            }
                            return inner.promise;
                        },
                        perform_list_by_full_name: function (full_name) {
                            var inner = $q.defer();
                            self.storage.users = {
                                current_page: 1,
                                items: []
                            };

                            Chat.search({
                                'q': full_name
                            }, function (success) {
                                var filter = {
                                    field: 'id',
                                    param: 'in',
                                    value: success.ids
                                };
                                var promise_list = self.users.perform_list(filter);
                                promise_list.then(function (success) {
                                    inner.resolve(success);
                                }, function (error) {
                                    inner.reject(error);
                                });

                            }, function (error) {
                                inner.reject(error);
                            });

                            return inner.promise;
                        },
                        perform_contacts: function (roster_ids, sub) {
                            /* sub is a name of array with users in the storage. Can be:
                             contacts, i_subscribers, o_subscribers
                            */
                            /* First we query roster, then users*/
                            var inner = $q.defer();
                            if (roster_ids.length == 0) {
                                inner.resolve([]);
                            } else {
                                var filter = {
                                    field: 'id',
                                    param: 'in',
                                    value: roster_ids,
                                };
                                var promise_u = self.users.get_list(null, null, filter);
                                promise_u.then(function (success) {
                                        self.storage[sub] = self.storage[sub].concat(success.items);
                                        inner.resolve();
                                    },
                                    function (error) {
                                        console.log(error);
                                        inner.reject(error);
                                    }
                                );
                            }
                            return inner.promise;
                        },
                    },
                    roster: {
                        get: function () {
                            /* Get user`s roster */
                            var inner = $q.defer();
                            pc.then(function (success) {
                                QB.chat.roster.get(function (res) {
                                    inner.resolve(res);
                                });
                            });
                            return inner.promise;
                        },
                        add: function (jidOrUserId) {
                            /* Subscribe on user */
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
                        confirm_user: function (user) {
                            var promise_confirm = self.roster.confirm(user.id);
                            promise_confirm.then(function (success) {
                                self.roster.confirm_transition(user);

                                var msg = self.credentials.full_name + ' accepted your friend request';
                                self.notify(user, msg);
                            });
                        },
                        reject_user: function (user) {
                            var promise_reject = self.roster.reject(user.id);
                            promise_reject.then(function (success) {
                                var index = self.storage.i_subscribers.indexOf(user);
                                console.log(index, 'rejecting');
                                self.storage.i_subscribers.splice(index, 1);

                                var msg = self.credentials.full_name + ' rejected your friend request';
                                self.notify(user, msg, 'warning');
                            });
                        },
                        unsubscribe_user: function (user, sub) {
                            if (!sub) {
                                sub = 'contacts';
                            }
                            var promise_remove = self.roster.remove(user.id);
                            promise_remove.then(function (success) {
                                var index = self.storage[sub].indexOf(user);
                                self.storage[sub].splice(index, 1);
                            });
                        },
                        subscribe_user: function (user) {
                            var promise_add = self.roster.add(user.id);
                            promise_add.then(function (success) {
                                var promise_user = self.users.get(user.id);
                                promise_user.then(function (success) {
                                    self.storage.o_subscribers.push({
                                        'user': success
                                    });
                                });
                                var msg = self.credentials.full_name + ' wants to add you to friend list';
                                self.notify(user, msg, 'info');
                            });
                        },
                        confirm_transition: function (user, sub) {
                            if (!sub) {
                                sub = 'i_subscribers';
                            }
                            var index = self.storage[sub].indexOf(user);
                            self.storage[sub].splice(index, 1);
                            self.storage.contacts.push({
                                'user': user
                            });
                        },
                        sort: function (roster) {
                            var sorted_roster = {
                                contacts: [],
                                i_subscribers: [],
                                o_subscribers: []
                            };
                            for (var property in roster) {
                                if (roster.hasOwnProperty(property)) {
                                    if (roster[property]['subscription'] == 'both') {
                                        sorted_roster.contacts.push(property);
                                    } else if (roster[property]['ask'] == 'subscribe') {
                                        sorted_roster.o_subscribers.push(property);
                                    } else {
                                        // roster[property]['subscription'] == 'none'
                                        //sorted_roster.i_subscribers.push(property);
                                    }
                                }
                            }
                            return sorted_roster;

                        },
                    },
                    send_message: function (dialog, body) {
                        if (body.length > 0) {
                            var p_send = self.messages.send_occupants(dialog, body);
                            p_send.then(function (success) {
                                // TODO
                            });
                        }
                    },
                    broadcast: function (signal) {
                        $rootScope.$broadcast(signal);
                    },
                    handlers: {
                        on_disconnected: function () {
                            Chat.destroy_session({
                                'token': self.credentials.token
                            });
                        },
                        on_message: function (user_id, msg) {
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
                                self.storage.i_subscribers.push({
                                    user: {
                                        id: success.id,
                                        full_name: (success.custom_data) ? success.custom_data : success.full_name,
                                    }
                                });
                            });
                        },
                        on_confirm_subscribe: function (user_id) {
                            var promise_user = self.users.get(user_id);
                            promise_user.then(function (success) {
                                var user = {
                                    id: success.id,
                                    full_name: (success.custom_data) ? success.custom_data : success.full_name,
                                };
                                self.roster.confirm_transition(user, 'o_subscribers');
                            });
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
                    },
                    reset_storage: function () {
                        for (var property in self.storage) {
                            if (self.storage.hasOwnProperty(property)) {
                                if (property == 'users') {
                                    self.storage[property] = {
                                        current_page: 1,
                                        items: []
                                    };
                                } else {
                                    self.storage[property] = [];
                                }
                            }
                        }
                    },
                    notify: function (user, msg, type) {
                        if (!type) {
                            type = 'success';
                        }

                        Chat.qid({
                            qid: user.id
                        }, function (success) {
                            var payload = {
                                message: msg,
                                user_id: success.id,
                                type: type,
                            };
                            Notification.save(payload, function (success) {
                            }, function (error) {
                                console.log('fail attempting to notifiy');
                            });
                        });

                    },
                    current_dialog: null,
                    storage: {
                        dialogs: [],
                        messages: [],
                        i_subscribers: [],
                        o_subscribers: [],
                        contacts: [],
                        users: {
                            current_page: 1,
                            items: []
                        },
                    },

                };
                // DIRTY!!!
                Quickblox.init();

                return Quickblox;
            }
        }
    ]);
