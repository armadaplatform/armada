var _fs = require('fs');
var _path = require('path');

var _endsWith = function(str, suffix) {
    return str.indexOf(suffix, str.length - suffix.length) !== -1;
};

exports.get_config_file_path = function(key){
    var config_paths = process.env.CONFIG_PATH;
    if ( typeof config_paths === 'undefined' || !config_paths) {
        return null;
    }

    var config_paths_array = config_paths.split(_path.delimiter);
    for (var idx = 0; idx < config_paths_array.length; ++idx) {
        var config_file_path = _path.join(config_paths_array[idx], key);
        if (_fs.existsSync(config_file_path)) {
            return config_file_path;
        }
    }
    return null;
};

exports.get_config = function(key, default_value) {
    if ( typeof default_value === 'undefined')
        default_value = null;

    var path = exports.get_config_file_path(key);
    if (!path) {
        return default_value;
    }

    var result = null;
    try {
        result = _fs.readFileSync(path);
    } catch (err) {
        console.error(err);
        return default_value;
    }

    if (_endsWith(key,'.json')) {
        result = JSON.parse(result);
    }
    return result;
};

exports.get_configs = function(key, default_value){
    if ( typeof default_value === 'undefined' )
        default_value = null;

    var path = exports.get_config_file_path(key);
    if (!path || !_fs.isDirectory(path)) {
        return default_value;
    }

    var result = {}

    try {
        var files = _fs.readdirSync(path);
        files.forEach(function(file_name){
            var file_path = _path.join(path, file_name);
            if (_fs.isFile(file_path)){
                result[file_name] = get_config(_path.join(key, file_name));
            }
        });

    } catch (err) {
        console.error(err);
    }
    return result;
};
