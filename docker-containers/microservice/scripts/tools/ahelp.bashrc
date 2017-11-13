function ahelp {
    echo -e "atools available:\n"

    local TAGS=("Usage" "Command" "Description")
    local dirtool="/opt/microservice/scripts/tools"
    local tag_printed=0

    while read p; do
        local tag_found=0
        if [[ "$p" =~ ^#([[:space:]]*)Command* ]]; then
            tag_printed=1
            tag_found=1
            local value="$(echo $p | sed -r 's/^\#(\s*)Command\:(\s*)//g')"
            echo -ne "  ${value}\n"
        fi
        if [[ "$p" =~ ^#([[:space:]]*)Description* ]]; then
            tag_printed=1
            tag_found=1
            local value="$(echo $p | sed -r 's/^\#(\s*)Description\:(\s*)//g')"
            echo -ne "     DESCRIPTION: ${value}\n"
        fi
        if [[ "$p" =~ ^#([[:space:]]*)Usage* ]]; then
            tag_printed=1
            tag_found=1
            local value="$(echo $p | sed -r 's/^\#(\s*)Usage\:(\s*)//g')"
            echo -ne "     USAGE:       ${value}\n"
        fi
        if [[ $tag_found -eq 0 ]]; then
            if [[ "$tag_printed" -eq 1 ]]; then
                echo -ne "\n"
                tag_printed=0
            fi
        fi
    done < <(cat $dirtool/*)
}

