#!/bin/bash
# Auto-detect and configure Java for the project
# This script finds the best Java version (21+) and sets it for the current session

echo -e "\033[0;36mSearching for Java installations...\033[0m"

# Search common Java installation directories
JAVA_SEARCH_PATHS=(
    "/usr/lib/jvm"
    "/Library/Java/JavaVirtualMachines"
    "/opt/homebrew/opt"
    "$HOME/.sdkman/candidates/java"
)

declare -A JAVA_INSTALLATIONS

for search_path in "${JAVA_SEARCH_PATHS[@]}"; do
    if [ -d "$search_path" ]; then
        for jdk_dir in "$search_path"/*/; do
            [ -d "$jdk_dir" ] || continue

            # Try to find java executable
            if [ -f "$jdk_dir/bin/java" ]; then
                java_path="$jdk_dir"
            elif [ -f "$jdk_dir/Contents/Home/bin/java" ]; then
                # macOS structure
                java_path="$jdk_dir/Contents/Home"
            else
                continue
            fi

            # Get version
            version=$("$java_path/bin/java" -version 2>&1 | head -n 1 | sed 's/.*version "\([0-9]*\).*/\1/')

            if [ -n "$version" ] && [ "$version" -ge 1 ] 2>/dev/null; then
                JAVA_INSTALLATIONS[$version]="$java_path"
            fi
        done
    fi
done

if [ ${#JAVA_INSTALLATIONS[@]} -eq 0 ]; then
    echo -e "\033[0;31mERROR: No Java installation found!\033[0m"
    echo -e "\033[0;33mPlease install Java 21 or higher:\033[0m"
    echo -e "\033[0;33m  - macOS: brew install openjdk@21\033[0m"
    echo -e "\033[0;33m  - Ubuntu/Debian: sudo apt install openjdk-21-jdk\033[0m"
    echo -e "\033[0;33m  - Or download from: https://adoptium.net/\033[0m"
    exit 1
fi

# Find best version (21+)
best_version=0
best_path=""

for version in "${!JAVA_INSTALLATIONS[@]}"; do
    if [ "$version" -ge 21 ] && [ "$version" -gt "$best_version" ]; then
        best_version=$version
        best_path="${JAVA_INSTALLATIONS[$version]}"
    fi
done

if [ "$best_version" -eq 0 ]; then
    echo -e "\033[0;31mERROR: Found Java installations, but none are version 21 or higher!\033[0m"
    echo -e "\033[0;33mFound versions:\033[0m"
    for version in "${!JAVA_INSTALLATIONS[@]}"; do
        echo -e "\033[0;33m  - Java $version: ${JAVA_INSTALLATIONS[$version]}\033[0m"
    done
    echo -e "\n\033[0;33mPlease install Java 21 or higher from https://adoptium.net/\033[0m"
    exit 1
fi

echo -e "\033[0;32mFound Java $best_version: $best_path\033[0m"

# Set environment variables
export JAVA_HOME="$best_path"
export PATH="$JAVA_HOME/bin:$PATH"

echo -e "\n\033[0;32mJava configured successfully!\033[0m"
echo -e "\033[0;36mJAVA_HOME = $JAVA_HOME\033[0m"

# Verify
echo -e "\n\033[0;36mVerifying Java version...\033[0m"
java -version

echo -e "\n\033[0;32mYou can now run your Python scripts. For example:\033[0m"
echo -e "\033[0;36m  cd personalized_shopping/shared_libraries/search_engine\033[0m"
echo -e "\033[0;36m  uv run python convert_product_file_format.py\033[0m"
echo -e "\n\033[0;33mNote: These environment variables are only set for the current shell session.\033[0m"
echo -e "\033[0;33mTo make them permanent, add the export commands to your ~/.bashrc or ~/.zshrc\033[0m"
