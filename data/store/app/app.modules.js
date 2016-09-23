var app = angular.module('app.main', [
    'ngAnimate',
    'ngSanitize',
    'ngAria',
    'ngCookies',
    'ngTouch',
    'ui.bootstrap',
    'asyncload.services',
    'pascalprecht.translate',
    'constants',
    'app.route',
    'auth.services',
    'navbar',
    'footer',
    'alert',
    'selfie',
    'grid',
    'common.directives',
]);
app.factory('httpRequestInterceptor', function($cookies) {
    return {
        request: function(config) {
            config.headers['X-Requested-With'] = 'XMLHttpRequest';
            config.headers['X-CSRFToken'] = $cookies.get('csrftoken');
            config.withCredentials = true;
            return config;
        }
    };
});
app.run(function($rootScope) {
    $rootScope.site = 'Atyichu';
    $rootScope.THEME = 'res/theme/';
    $rootScope.PATH = 'app/';
    $rootScope.alerts = [];
    $rootScope.app = {
        navbarHeaderColor: 'bg-black',
        navbarCollapseColor: 'bg-white-only',
        asideColor: 'bg-black',
        headerFixed: true,
        asideFixed: false,
        asideFolded: false,
        asideDock: false,
        hideAside: false,
        container: false
    };
});
app.config(function ($httpProvider) {
    $httpProvider.interceptors.push('httpRequestInterceptor');
    $httpProvider.useApplyAsync(true);
});
app.config(function($resourceProvider) {
  $resourceProvider.defaults.stripTrailingSlashes = false;
});
app.config(['$locationProvider', function($locationProvider){
    //$locationProvider.html5Mode(true);
    $locationProvider.hashPrefix('!');
}]);

app.config(['$translateProvider', function ($translateProvider) {
    $translateProvider.translations('en', {
        'NO_PERMISSION': 'You have not enough privileges perform this action.',
        'ERROR': 'Error',
        'CONFIRM': 'Are you sure you want perform this action?',
        'FAIL': 'Fail',
        'SUCCESS': 'Success!',
        'LOAD_MORE': 'Load more',
        'COMMON': {
            'HOME': {
                'TITLE': 'Welcome!',
            },
            'ERROR': {
                '404': '404: Page Not Found',
            }
        },
        'FORM': {
            'CANCEL': 'Cancel',
            'SUBMIT': 'Submit',
            'ADD': 'Add',
            'DELETE': 'Delete',
            'WAIT': 'Please wait...',
            'UPDATE': 'Update',
        },
        'AUTHENTICATION': {
            'REQUIRED': 'Please, log in.',
            'SUCCESS': 'Welcome back!',
            'ERROR': 'Authentication error',
            'LOGOUT': 'Good by',

        },
        'NAVBAR': {
            'MODAL': {
                'CLOSE': 'Close',
                'TITLE': 'Sign in',
                'USERNAME': 'Username',
                'PASSWORD': 'Password',
                'ENTER': 'Enter',
                'FORGOT': 'I forgot my password',
            },
            'TOGGLE_NAV': 'Toggle Navigation',
            'LOGGED': 'You logged as {{username}}',
            'PROFILE': 'My profile',
            'STORE': 'My store',
            'LOGOUT': 'Logout',
            'SIGN': 'Sign',
            'SIGN_IN': 'Sign in',
            'CHANGE_PASSWORD': 'Change password',
        },
        'ASIDE': {
            'CHAT': 'Chat',
            'NAV': {
                'HEADER': 'Navigation'
            },
            'DASHBOARD': 'Dashboard',
            'PHOTO': {
                'TITLE': 'Photos',
                'ALL_GROUPS': 'All Groups',
                'FOLLOWING_GROUPS': 'Following Groups',
                'MY_GROUPS': 'My Wardrobes',
                'ADD_GROUP': 'Add A Wardrobe',
                'DISCOVERY': 'Discovery',
                'LIKED': 'Favorite',
            },
            'ARTICLE': {
                'TITLE': 'Article',
                'MY': 'My Articles',
                'ADD': 'Add An Article',
            },            
            'COMMODITY': {
                'TITLE': 'Commodity',
                'MY': 'My Commodities',
                'ADD': 'Add A Commodity',
            },
            'STORE': {
                'TITLE': 'My Store',
                'OVERVIEW': 'Overview',
                'EDIT': 'Edit',
                'CREATE': 'Create',
            },
        },
        'STORE': {
            'CREATE': {
                'HEADER': 'Create a store',
                'ALREADY': 'You already have a store',
                'SUCCESS': 'Store has been created',
            },
            'UPDATE': {
                'HEADER': 'Edit your store',
                'SUCCESS': 'Your store information has been updated.',
                'FAIL': 'Fail trying update.',
                'UPDATE_PHOTO': 'Update photo',
                'UPDATE_DATA': 'Update data',
            },
            'FORM': {
                'BRAND_NAME': 'Brand name',
                'STORE_NAME': 'Store Name',
                'INTRODUCTION': 'Introduction',
                'STATE': 'State',
                'CITY': 'City',
                'DISTRICT': 'District',
                'ADDRESS': 'Address',
                'LATITUDE': 'Latitude',
                'LONGITUDE': 'Longitude',
                'STREET': 'Street',
                'STREET_NO': 'Street number',
                'BUILD_NAME': 'Building name',
                'BUILD_NO': 'Building number',
                'APT': 'Apartments',
                'LOGO': 'Logo',
                'POST': 'Post',
                'CROP': 'Crop',
                'SUBMIT': 'Submit',
                'CANCEL': 'Cancel',
                'LOCATION': 'Location',
                'NO_PHOTO': 'No photo',
                'POSTER': 'Poster',
                'DESCRIPTION': 'Description',
                'START_DATE': 'Start date',
                'NAME': 'Name',
                'POST': 'Post',
                'PHOTO': 'Logo',
            },
            'MY': {
                'HEADER': 'Your store overview',
                'ADD_BRAND': 'Add a brand',
                'ADD_PROMOTION': 'Add a promotion',
                'ADD_COLOR': 'Add a color',
                'ADD_SIZE': 'Add a size',
                'ADD_PROMOTION': 'Add a promotion'
            },
            'MODAL': {
                'TITLE_PLACE': 'Enter a title',
                'PRIORITY_PLACE': 'Enter a priority',
                'COLOR_PLACE': 'Enter a html (hex) color',
            },
         },
        'GROUP': {
            'CREATE': {
                'HEADER': 'Create a wardrobe',
            },
            'LIST': {
                'NO_GROUPS': 'No groups',
                'UPLOAD': 'Upload a photo',
                'FOLLOW': 'Follow this group',
            },
            'MANAGE': {
                    'HEADER': 'Edit a wardrobe',
                    'MEMBER_EXCLUDED': 'Collaborator has been excluded',
                    'TAG_REMOVED': 'Tag has been removed',
            },
            'FORM': {
                'TITLE': 'Title',
                'DESCRIPTION': 'Description',
                'IS_PRIVATE': 'Private',
                'MEMBERS': 'Collaborators',
                'FILE': 'File',
                'NO_MEMBERS': 'You did not choose any collaborator.',
            },
            'PHOTO_ADD': {
                'HEADER': 'Upload a photo to {{title}}',
                'SUCCESS': 'Photo has been added to your group',
            },
            'PHOTO_LIST': {
                'UPLOAD': 'Upload a photo',
                'TAGS': 'Tags',
                'MEMBERS': 'Collaborators',
                'PHOTO_LIKED': 'You have liked the photo already',
                'SAVED_TO': 'Saved to',
                'SAVED_FROM': 'Saved from',
            }
        },
        'PHOTO': {
            'CLONE': {
                'HEADER': 'Share a photo',
                'CHOOSE_GROUP': 'Choose a group',
                'CLONED': 'Photo has been shared.',
            },
            'DETAIL': {
                'LIKE': 'Like',
                'REPLY': 'Reply',
                'DELETED': 'Photo has been deleted.',
                'SIMILAR': 'Similar Photos',
                'EMPTY_COMMENT': 'You have to type something.',
                'COMMENT': 'Your comment is posted',
            },
            'EDIT': {
                'HEADER': 'Edit photo data',
                'DATA_UPDATED': 'Data has been updated',
                'ADD_LINK': 'You can add up to three commodity links',
                'LINK_REMOVED': 'Link to the commodity has been removed',
                'LINKS': 'Links to commodities',
                'NEW_LINKS': 'Links to bind',
            },
            'LIST': {
                'HEADER': 'Photo list',
                'TAKE_SNAPSHOT': 'Take a snapshot',
                'NOT_WORK': 'Will not work',
                'CREATED': 'Photo has been created.',
            },
            'FORM': {
                'TITLE': 'Title',
                'DESCRIPTION': 'Description',
            }
        },
        'ARTICLE': {
            'CREATE': {
                'HEADER': 'Add an article',
                'SUCCESS': 'A new article has been added to your store',
                'NO_COLOR': 'Required color is missed? Then send us your extra color',
            },
            'UPDATE': {
                'HEADER': 'Update a article',
                'PHOTO_HEADER': 'Article`s photo',
                'PHOTO_ADD': 'Add a new photo',
                'DATA_HEADER': 'Update a article data',
                'SUCCESS': 'Article has been updated',
            },
        },                
        'COMMODITY': {
            'CREATE': {
                'HEADER': 'Add a commodity',
                'SUCCESS': 'A new commodity has been added to your store',
                'NO_COLOR': 'Required color is missed? Then send us your extra color',
            },
            'UPDATE': {
                'HEADER': 'Update a commodity',
                'PHOTO_HEADER': 'Commodity`s photo',
                'PHOTO_ADD': 'Add a new photo',
                'DATA_HEADER': 'Update a commodity data',
                'SUCCESS': 'Commodity has been updated',
            },
            'MY_LIST': {
                'HEADER': 'My store`s commodities',
                'TABLE': {
                    'COVER': 'Cover',
                    'NAME': 'Name',
                    'ACTIONS': 'Actions',
                },
            },
            'DETAIL': {
                'HEADER': 'Commodity',
            },
            'FORM': {
                'EMPTY': 'Please, choose one from the list',
                'TITLE': 'Title',
                'CATEGORY': 'Catalog',
                'KIND': 'Kind',
                'BRAND': 'Brand',
                'COLOR': 'Color',
                'COLORS': 'Colors',
                'SIZE': 'Size',
                'SIZES': 'Sizes',
                'SEASON': 'Season',
                'YEAR': 'Year',
                'EXTRA_COLOR': 'Extra color',
                'COLOR_PIC': 'Sample of color',
                'FILES': 'Photos',
                'AMOUNT': 'Amount',
                'STOCKS': 'Stocks',
                'ANOTHER_STOCK': 'Add another Stock',
                'DESCRIPTION': 'Description',
            },
            'SEASONS': {
                'WINTER': 'Winter',
                'SPRING': 'Spring',
                'SUMMER': 'Summer',
                'AUTUMN': 'Autumn',
            },
        },
    });

    $translateProvider.translations('zh', {
        'NO_PERMISSION': 'You have not enough privileges perform this action.',
        'ERROR': 'Error',
        'CONFIRM': 'Are you sure you want perform this action?',
        'FAIL': 'Fail',
        'SUCCESS': 'Success!',
        'LOAD_MORE': 'Load more',
        'COMMON': {
            'HOME': {
                'TITLE': 'Welcome!',
            },
        },
        'FORM': {
            'CANCEL': 'Cancel',
            'SUBMIT': 'Submit',
            'ADD': 'Add',
            'DELETE': 'Delete',
            'WAIT': 'Please wait...',
            'UPDATE': 'Update',
        },
        'AUTHENTICATION': {
            'REQUIRED': 'Please, log in.',
            'SUCCESS': 'Welcome back!',
            'ERROR': 'Authentication error',
            'LOGOUT': 'Good by',

        },
        'NAVBAR': {
            'MODAL': {
                'CLOSE': 'Close',
                'TITLE': 'Sign in',
                'USERNAME': 'Username',
                'PASSWORD': 'Password',
                'ENTER': 'Enter',
                'FORGOT': 'I forgot my password',
            },
            'TOGGLE_NAV': 'Toggle Navigation',
            'LOGGED': 'You are logged as {{username}}',
            'PROFILE': 'My profile',
            'STORE': 'My store',
            'LOGOUT': 'Logout',
            'SIGN': 'Sign',
            'SIGN_IN': 'Sign in',
            'CHANGE_PASSWORD': 'Change password',
        },
        'ASIDE': {
            'CHAT': 'Chat',
            'NAV': {
                'HEADER': 'Navigation'
            },
            'DASHBOARD': 'Dashboard',
            'PHOTO': {
                'TITLE': 'Photos',
                'MY_GROUPS': 'My Wardrobes',
                'ADD_GROUP': 'Add A Wardrobe',
                'DISCOVERY': 'Discovery',
                'LIKED': 'Favorite',
            },
            'COMMODITY': {
                'TITLE': 'Commodity',
                'MY': 'My Commodities',
                'ADD': 'Add A Commodity',
            },
            'STORE': {
                'TITLE': 'My Store',
                'OVERVIEW': 'Overview',
                'EDIT': 'Edit',
                'CREATE': 'Create',
            },
        },
        'STORE': {
            'CREATE': {
                'HEADER': 'Create a store',
                'ALREADY': 'You already have a store',
                'SUCCESS': 'Store has been created',
            },
            'UPDATE': {
                'HEADER': 'Edit your store',
                'SUCCESS': 'Your store information has been updated.',
                'FAIL': 'Fail trying update.',
                'UPDATE_PHOTO': 'Update photo',
                'UPDATE_DATA': 'Update data',
            },
            'FORM': {
                'BRAND_NAME': 'Brand name',
                'STORE_NAME': 'Store Name',
                'INTRODUCTION': 'Introduction',
                'STATE': 'State',
                'CITY': 'City',
                'DISTRICT': 'District',
                'ADDRESS': 'Address',
                'LATITUDE': 'Latitude',
                'LONGITUDE': 'Longitude',
                'STREET': 'Street',
                'STREET_NO': 'Street number',
                'BUILD_NAME': 'Building name',
                'BUILD_NO': 'Building number',
                'APT': 'Apartments',
                'LOGO': 'Logo',
                'POST': 'Post',
                'CROP': 'Crop',
                'SUBMIT': 'Submit',
                'CANCEL': 'Cancel',
                'LOCATION': 'Location',
                'NO_PHOTO': 'No photo',
                'POSTER': 'Poster',
                'DESCRIPTION': 'Description',
                'START_DATE': 'Start date',
                'NAME': 'Name',
                'POST': 'Post',
                'PHOTO': 'Logo'
            },
            'MY': {
                'HEADER': 'Your store overview',
                'ADD_BRAND': 'Add a brand',
                'ADD_PROMOTION': 'Add a promotion',
                'ADD_COLOR': 'Add a color',
                'ADD_SIZE': 'Add a size',
                'ADD_PROMOTION': 'Add a promotion'
            },
            'MODAL': {
                'TITLE_PLACE': 'Enter a title',
                'PRIORITY_PLACE': 'Enter a priority',
                'COLOR_PLACE': 'Enter a html (hex) color',
            },
         },
        'GROUP': {
            'CREATE': {
                'HEADER': 'Create a wardrobe',
            },
            'LIST': {
                'NO_GROUPS': 'No groups',
                'UPLOAD': 'Upload a photo',
            },
            'MANAGE': {
                    'HEADER': 'Edit a wardrobe',
                    'MEMBER_EXCLUDED': 'Collaborator has been excluded',
                    'TAG_REMOVED': 'Tag has been removed',
            },
            'FORM': {
                'TITLE': 'Title',
                'DESCRIPTION': 'Description',
                'IS_PRIVATE': 'Private',
                'MEMBERS': 'Collaborators',
                'FILE': 'File',
                'NO_MEMBERS': 'You did not choose any collaborator.',
            },
            'PHOTO_ADD': {
                'HEADER': 'Upload a photo to {{title}}',
                'SUCCESS': 'Photo has been added to your group',
            },
            'PHOTO_LIST': {
                'UPLOAD': 'Upload a photo',
                'TAGS': 'Tags',
                'MEMBERS': 'Collaborators',
                'PHOTO_LIKED': 'You have liked the photo already',
                'SAVED_TO': 'Saved to',
                'SAVED_FROM': 'Saved from',
            }
        },
        'PHOTO': {
            'CLONE': {
                'HEADER': 'Share a photo',
                'CHOOSE_GROUP': 'Choose a group',
                'CLONED': 'Photo has been shared.',
            },
            'DETAIL': {
                'LIKE': 'Like',
                'REPLY': 'Reply',
                'DELETED': 'Photo has been deleted.',
                'SIMILAR': 'Similar Photos',
                'EMPTY_COMMENT': 'You have to type something.',
                'COMMENT': 'Your comment is posted',
            },
            'EDIT': {
                'HEADER': 'Edit photo data',
                'DATA_UPDATED': 'Data has been updated',
                'ADD_LINK': 'You can add up to three commodity links',
                'LINK_REMOVED': 'Link to the commodity has been removed',
                'LINKS': 'Links to commodities',
                'NEW_LINKS': 'Links to bind',
            },
            'LIST': {
                'HEADER': 'Photo list',
                'TAKE_SNAPSHOT': 'Take a snapshot',
                'NOT_WORK': 'Will not work',
                'CREATED': 'Photo has been created.',
            },
            'FORM': {
                'TITLE': 'Title',
                'DESCRIPTION': 'Description',
                'GROUP': 'Group',
            }
        },
        'ARTICLE': {
            'CREATE': {
                'HEADER': 'Add an article',
                'SUCCESS': 'A new article has been added to your store',
                'NO_COLOR': 'Required color is missed? Then send us your extra color',
            },
            'UPDATE': {
                'HEADER': 'Update a article',
                'PHOTO_HEADER': 'Article`s photo',
                'PHOTO_ADD': 'Add a new photo',
                'DATA_HEADER': 'Update a article data',
                'SUCCESS': 'Article has been updated',
            },
        },        
        'COMMODITY': {
            'CREATE': {
                'HEADER': 'Add a commodity',
                'SUCCESS': 'A new commodity has been added to your store',
                'NO_COLOR': 'Required color is missed? Then send us your extra color',
            },
            'UPDATE': {
                'HEADER': 'Update a commodity',
                'PHOTO_HEADER': 'Commodity`s photo',
                'PHOTO_ADD': 'Add a new photo',
                'DATA_HEADER': 'Update a commodity data',
                'SUCCESS': 'Commodity has been updated',
            },
            'MY_LIST': {
                'HEADER': 'My store`s commodities',
                'TABLE': {
                    'COVER': 'Cover',
                    'NAME': 'Name',
                    'ACTIONS': 'Actions',
                },
            },
            'DETAIL': {
                'HEADER': 'Commodity',
            },
            'FORM': {
                'EMPTY': 'Please, choose one from the list',
                'TITLE': 'Title',
                'CATEGORY': 'Catalog',
                'KIND': 'Kind',
                'BRAND': 'Brand',
                'COLOR': 'Color',
                'COLORS': 'Colors',
                'SIZE': 'Size',
                'SIZES': 'Sizes',
                'SEASON': 'Season',
                'YEAR': 'Year',
                'EXTRA_COLOR': 'Extra color',
                'COLOR_PIC': 'Sample of color',
                'FILES': 'Photos',
                'AMOUNT': 'Amount',
                'STOCKS': 'Stocks',
                'ANOTHER_STOCK': 'Add another Stock',
                'DESCRIPTION': 'Description',
            },
            'SEASONS': {
                'WINTER': 'Winter',
                'SPRING': 'Spring',
                'SUMMER': 'Summer',
                'AUTUMN': 'Autumn',
            },
        },
    });


  $translateProvider.preferredLanguage('en');
}]);