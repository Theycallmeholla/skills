#!/usr/bin/env bash
set -euo pipefail

# Skills Repo Push — sync from repo to local ~/.claude/skills
# Direction: repo → local (opposite of skills-repo-sync)
# Default: dry-run (requires --apply to write)

# Paths with environment overrides
REPO_DIR="${REPO_DIR:-/Users/cursivemedia/skills}"
LOCAL_DIR="${LOCAL_DIR:-$HOME/.claude/skills}"

# Files that accumulate user data locally and must NEVER be overwritten by the repo's
# template version. Space-separated glob patterns, relative to a skill folder.
# Example: blog-topic-interview/references/opinion-bank.md holds the author's real
# positions; the repo copy is a blank template. Overwriting it is silent data loss.
PRESERVE_GLOBS="${PRESERVE_GLOBS:-references/opinion-bank.md references/*-bank.md state.json}"

BACKUP_DIR="/tmp/skills-push-backup-$(date +%Y%m%d-%H%M%S)"

# Is this path (relative to a skill folder) a preserved state file?
is_preserved() {
    local rel="$1" glob
    for glob in $PRESERVE_GLOBS; do
        # shellcheck disable=SC2053
        [[ "$rel" == $glob ]] && return 0
    done
    return 1
}

# List preserved files that exist locally for a given skill
preserved_files() {
    local skill="$1" f rel
    [[ -d "$LOCAL_DIR/$skill" ]] || return 0
    while IFS= read -r f; do
        rel="${f#"$LOCAL_DIR/$skill/"}"
        is_preserved "$rel" && printf '%s\n' "$rel"
    done < <(find "$LOCAL_DIR/$skill" -type f -not -name '.*' 2>/dev/null)
}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
RESET='\033[0m'

# Parse arguments
APPLY=false
SKILL_FILTER=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --apply)
            APPLY=true
            shift
            ;;
        *)
            SKILL_FILTER+=("$1")
            shift
            ;;
    esac
done

# Verify paths exist
if [[ ! -d "$REPO_DIR/skills" ]]; then
    echo -e "${RED}Error: Repo skills directory not found: $REPO_DIR/skills${RESET}" >&2
    exit 1
fi

if [[ ! -d "$LOCAL_DIR" ]]; then
    echo -e "${YELLOW}Warning: Local skills directory not found: $LOCAL_DIR${RESET}"
    echo "Creating directory..."
    mkdir -p "$LOCAL_DIR"
fi

# Function to calculate file/line stats for a directory
get_dir_stats() {
    local dir="$1"
    local file_count line_count

    if [[ ! -d "$dir" ]]; then
        echo "0 files, 0 lines"
        return
    fi

    file_count=$(find "$dir" -type f -not -name '.*' 2>/dev/null | wc -l | tr -d ' ')
    line_count=$(find "$dir" -type f -not -name '.*' -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')
    line_count="${line_count:-0}"

    echo "$file_count files, $line_count lines"
}

# Function to compare two directories
dirs_differ() {
    local dir1="$1"
    local dir2="$2"

    # If one doesn't exist, they differ
    [[ ! -d "$dir1" ]] && return 0
    [[ ! -d "$dir2" ]] && return 0

    # Compare contents excluding hidden files
    if ! diff -rq --exclude=".*" "$dir1" "$dir2" >/dev/null 2>&1; then
        return 0
    fi

    return 1
}

# Arrays to track skills
declare -a NEW_SKILLS=()
declare -a CHANGED_SKILLS=()
declare -a IDENTICAL_SKILLS=()
declare -a PROCESSED_SKILLS=()

# Scan repo skills
echo -e "${BOLD}Scanning skills repo: $REPO_DIR/skills${RESET}"
echo

# Build skill list (filtered or all)
if [[ ${#SKILL_FILTER[@]} -gt 0 ]]; then
    # Use filtered list
    for skill in "${SKILL_FILTER[@]}"; do
        if [[ -d "$REPO_DIR/skills/$skill" ]]; then
            PROCESSED_SKILLS+=("$skill")
        else
            echo -e "${YELLOW}Warning: Skill not found in repo: $skill${RESET}"
        fi
    done
else
    # Get all skills from repo
    for skill_path in "$REPO_DIR"/skills/*/; do
        [[ -d "$skill_path" ]] || continue
        skill_name=$(basename "$skill_path")
        PROCESSED_SKILLS+=("$skill_name")
    done
fi

# Process each skill
for skill in "${PROCESSED_SKILLS[@]}"; do
    repo_path="$REPO_DIR/skills/$skill"
    local_path="$LOCAL_DIR/$skill"

    if [[ ! -d "$local_path" ]]; then
        NEW_SKILLS+=("$skill")
    elif dirs_differ "$repo_path" "$local_path"; then
        CHANGED_SKILLS+=("$skill")
    else
        IDENTICAL_SKILLS+=("$skill")
    fi
done

# Report summary
echo -e "${BOLD}Summary:${RESET}"
echo -e "  ${GREEN}NEW:${RESET} ${#NEW_SKILLS[@]} skills"
echo -e "  ${YELLOW}CHANGED:${RESET} ${#CHANGED_SKILLS[@]} skills"
echo -e "  ${BLUE}IDENTICAL:${RESET} ${#IDENTICAL_SKILLS[@]} skills (skipped)"
echo

# Show details for NEW skills
if [[ ${#NEW_SKILLS[@]} -gt 0 ]]; then
    echo -e "${GREEN}NEW skills to add:${RESET}"
    for skill in "${NEW_SKILLS[@]}"; do
        stats=$(get_dir_stats "$REPO_DIR/skills/$skill")
        echo -e "  + $skill ($stats)"
    done
    echo
fi

# Show details for CHANGED skills
if [[ ${#CHANGED_SKILLS[@]} -gt 0 ]]; then
    echo -e "${YELLOW}CHANGED skills to update:${RESET}"
    for skill in "${CHANGED_SKILLS[@]}"; do
        repo_stats=$(get_dir_stats "$REPO_DIR/skills/$skill")
        local_stats=$(get_dir_stats "$LOCAL_DIR/$skill")
        echo -e "  ≠ $skill"
        echo -e "    repo:  $repo_stats"
        echo -e "    local: $local_stats"

        # Show brief diff summary
        if [[ -f "$REPO_DIR/skills/$skill/SKILL.md" ]] && [[ -f "$LOCAL_DIR/$skill/SKILL.md" ]]; then
            diff_lines=$(diff -u "$LOCAL_DIR/$skill/SKILL.md" "$REPO_DIR/skills/$skill/SKILL.md" 2>/dev/null | wc -l | tr -d ' ')
            if [[ "$diff_lines" -gt 0 ]]; then
                echo -e "    SKILL.md differs ($diff_lines diff lines)"
            fi
        fi

        while IFS= read -r rel; do
            [[ -n "$rel" ]] && echo -e "    ${GREEN}keeping local${RESET} $rel (local state, not overwritten)"
        done < <(preserved_files "$skill")
    done
    echo
fi

# Check if any changes needed
TOTAL_CHANGES=$((${#NEW_SKILLS[@]} + ${#CHANGED_SKILLS[@]}))

if [[ $TOTAL_CHANGES -eq 0 ]]; then
    echo -e "${GREEN}✓ Local skills are up to date with repo${RESET}"
    exit 0
fi

# Create tarball of NEW+CHANGED skills
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
TARBALL="/tmp/skills-push-${TIMESTAMP}.tar.gz"

echo -e "${BOLD}Creating tarball for Claude app upload...${RESET}"
(
    cd "$REPO_DIR/skills"
    tar czf "$TARBALL" \
        ${NEW_SKILLS[@]+"${NEW_SKILLS[@]}"} \
        ${CHANGED_SKILLS[@]+"${CHANGED_SKILLS[@]}"} 2>/dev/null
)
echo -e "  Tarball: ${BLUE}$TARBALL${RESET}"
echo -e "  Size: $(du -h "$TARBALL" | cut -f1)"
echo

# Apply changes if requested
if [[ "$APPLY" == true ]]; then
    echo -e "${BOLD}Applying changes...${RESET}"

    # Copy NEW skills
    for skill in "${NEW_SKILLS[@]}"; do
        echo -e "  ${GREEN}+ Adding $skill${RESET}"
        cp -R "$REPO_DIR/skills/$skill" "$LOCAL_DIR/"
    done

    # Update CHANGED skills
    mkdir -p "$BACKUP_DIR"
    for skill in "${CHANGED_SKILLS[@]}"; do
        echo -e "  ${YELLOW}≠ Updating $skill${RESET}"

        # full backup before any destructive step
        cp -R "$LOCAL_DIR/$skill" "$BACKUP_DIR/"

        # stash local state files, restore them over the fresh copy
        stash="$(mktemp -d)"
        while IFS= read -r rel; do
            [[ -n "$rel" ]] || continue
            mkdir -p "$stash/$(dirname "$rel")"
            cp "$LOCAL_DIR/$skill/$rel" "$stash/$rel"
        done < <(preserved_files "$skill")

        rm -rf "${LOCAL_DIR:?}/${skill:?}"
        cp -R "$REPO_DIR/skills/$skill" "$LOCAL_DIR/"

        while IFS= read -r rel; do
            [[ -n "$rel" ]] || continue
            mkdir -p "$LOCAL_DIR/$skill/$(dirname "$rel")"
            cp "$stash/$rel" "$LOCAL_DIR/$skill/$rel"
            echo -e "    ${GREEN}restored local${RESET} $rel"
        done < <(cd "$stash" && find . -type f | sed 's|^\./||')
        rm -rf "$stash"
    done
    echo -e "  backup of replaced skills: ${BLUE}$BACKUP_DIR${RESET}"

    echo
    echo -e "${GREEN}✓ Successfully synchronized $TOTAL_CHANGES skills${RESET}"
    echo
    echo -e "${BOLD}Next steps:${RESET}"
    echo "1. Extract tarball for Claude app upload:"
    echo -e "   ${BLUE}tar xzf $TARBALL${RESET}"
    echo "2. Upload extracted skills through Claude app UI"
else
    # Dry-run mode
    echo -e "${BOLD}DRY RUN — no skills were modified${RESET}"
    echo "(the tarball above was written; nothing under $LOCAL_DIR was touched)"
    echo
    echo "To apply these changes, run:"
    echo -e "  ${BLUE}$0 --apply${RESET}"
    if [[ ${#SKILL_FILTER[@]} -gt 0 ]]; then
        echo -e "  ${BLUE}$0 --apply ${SKILL_FILTER[*]}${RESET}"
    fi
    echo
    echo "The tarball contains NEW+CHANGED skills for manual Claude app upload."
fi

# Verify no symlinks in output (safety check)
if [[ "$APPLY" == true ]]; then
    symlink_count=$(find "$LOCAL_DIR" -type l 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$symlink_count" -gt 0 ]]; then
        echo -e "${YELLOW}Warning: Found $symlink_count symlinks in local skills directory${RESET}"
        echo "This may indicate installation issues. Check with: find $LOCAL_DIR -type l"
    fi
fi
