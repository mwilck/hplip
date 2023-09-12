#! /bin/bash
: "${TARGET:=$PWD}"

CLEANUP=":"
trap 'echo cleanup: "$CLEANUP" >&2; eval "$CLEANUP"' EXIT
trap 'echo error in $BASH_COMMAND >&2; exit 1' ERR
set -E

unpack_hplip() {
    ver=$1
    CLEANUP='rm -f "/tmp/hplip-$ver.tar.gz";'"$CLEANUP"
    curl -L -o "/tmp/hplip-$ver.tar.gz" \
	 "https://sourceforge.net/projects/hplip/files/hplip/$ver/hplip-$ver.tar.gz/download"
    TD=$(mktemp -d /tmp/hplip-XXXXXX)
    CLEANUP='rm -rf "$TD";'"$CLEANUP"
    tar xz -C "$TD" -f "/tmp/hplip-$ver.tar.gz"
    rsync -ai --delete --exclude=.git\* --exclude=git-helpers "$TD/hplip-$ver/" "$TARGET"
    find . -name '*.gz' | xargs gzip -dvf 2>&1 | tee "$TD/uncompressed.txt"
    sed -i 's/\.gz:.*//' "$TD/uncompressed.txt"
    cat git-helpers/uncompressed.txt "$TD/uncompressed.txt" | sort -u >"$TD/new.txt"
    cp "$TD/new.txt" git-helpers/uncompressed.txt
    git add .
    git commit -m "hplip $ver"
    git tag "$ver"
}

[[ "$1" ]]
unpack_hplip "$1"
