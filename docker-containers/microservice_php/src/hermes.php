<?php

class Hermes
{
    static function get_config_file_path($filename, $default_path = '')
    {
        $config_path = getenv('CONFIG_PATH');
        $config_paths = explode(':', $config_path);
        if ($default_path)
        {
            $config_paths []= $default_path;
        }

        foreach ($config_paths as $path)
        {
            if (file_exists($path.'/'.$filename))
            {
                return $path.'/'.$filename;
            }
        }

        return null;
    }

    static function require_file($filename, $default_path = '')
    {
        $config_file_path = self::get_config_file_path($filename, $default_path);
        if ($config_file_path !== null) {
            return require($config_file_path);
        }
        return null;
    }
};
