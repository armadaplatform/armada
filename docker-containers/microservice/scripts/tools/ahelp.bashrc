function ahelp {
    echo -e "atools available:\n"

    local TAGS=("Usage" "Command" "Description")
    local TAGS_INDENT=(5 0 5)
    local TAGS_VISIBLE=(1 0 1)
    local DIRTOOL="/opt/microservice/scripts/tools"
    local tag_printed=0

    while read p; do
        local tag_found=0
        local tag_index=0
        for tag in ${TAGS[@]}; do
            local match="^#([[:space:]]*)$tag*"
            if [[ $p =~ $match ]]; then
                tag_printed=1
                tag_found=1
                local value="$(echo $p | sed -r "s/^\\#(\\s*)$tag\\:(\\s*)//g")"
                if [[ ${TAGS_VISIBLE[$tag_index]} -eq 1 ]]; then
                    value="${TAGS[$tag_index]^^}: $value"
                fi
                echo "$(printf "%-${TAGS_INDENT[$tag_index]}s" " ")"$value
            fi
            let 'tag_index = tag_index + 1'
        done
        if [[ $tag_found -eq 0 ]]; then
            if [[ "$tag_printed" -eq 1 ]]; then
                echo -ne "\n"
                tag_printed=0
            fi
        fi
    done < <(cat $DIRTOOL/*)
}
