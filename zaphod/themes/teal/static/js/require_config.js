// Common RequireJS config
// Used only in development and for optimization
var require = {
  baseUrl: '/_light/js/vendor',

  paths: {
    'light': '/_light/js'
  },

  shim: {
    underscore: {
      exports: '_',
      init: function () {
         this._.templateSettings = {
          evaluate    : /\{\{(.+?)\}\}/g,
          interpolate : /\{\{=(.+?)\}\}/g,
          escape      : /\{\{-(.+?)\}\}/g,
        };
      }
    },

    'd3': {
      'exports': 'd3'
    },

    'bootstrap3/affix': ['jquery'],
    'bootstrap3/alert': ['jquery'],
    'bootstrap3/button': ['jquery'],
    'bootstrap3/carousel': ['jquery'],
    'bootstrap3/collapse': ['jquery', 'bootstrap3/transition'],
    'bootstrap3/dropdown': ['jquery'],
    'bootstrap3/modal': ['jquery'],
    'bootstrap3/popover': ['jquery', 'bootstrap3/tooltip'],
    'bootstrap3/scrollspy': ['jquery'],
    'bootstrap3/tab': ['jquery'],
    'bootstrap3/tooltip': ['jquery'],
    'bootstrap3/transition': ['jquery'],
  }
};
