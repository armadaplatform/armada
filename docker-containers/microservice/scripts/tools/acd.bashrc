# Command:      acd
# Description:  changes cwd to /opt/$IMAGE_NAME/[DIRECTORY]
# Usage:        acd [DIRECTORY]
function acd {
    cd /opt/${IMAGE_NAME}/${1}
}
