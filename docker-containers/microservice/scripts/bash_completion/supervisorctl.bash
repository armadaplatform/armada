_supervisorctl_action() {

    local all_options=(start restart stop status)
    local command="supervisorctl"

    local current=${COMP_WORDS[COMP_CWORD]}
    local previous=${COMP_WORDS[COMP_CWORD-1]}

    if [[ "${all_options[@]}" =~ "$current" && "$previous" == "$command" ]]; then
       COMPREPLY=($(compgen -W "$(echo ${all_options[@]})" -- $current) )
    fi

    if [[ "${all_options[@]}" =~ "$previous" ]]; then
        COMPREPLY=($(compgen -W "$(supervisorctl status | awk '{print $1}')" -- $current) )
    fi

    return 0
}

complete -F _supervisorctl_action supervisorctl
