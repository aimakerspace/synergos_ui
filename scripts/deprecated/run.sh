# read -p "Please enter your username: " USERNAME
# echo $USERNAME

# read -p "Please enter your password: " -s PASSWORD
# echo $PASSWORD

### Temporary fix until all Synergos repositories are made public! ###
git config --global credential.helper cache

declare -A CORE_REPOSITORIES
CORE_REPOSITORIES['synergos']="https://gitlab.int.aisingapore.org/aims/federatedlearning/synergos.git"
CORE_REPOSITORIES['synergos_director']="https://gitlab.int.aisingapore.org/aims/federatedlearning/synergos_director.git"
CORE_REPOSITORIES['synergos_ttp']="https://gitlab.int.aisingapore.org/aims/federatedlearning/synergos_ttp.git"

for syn_name in "${!CORE_REPOSITORIES[@]}";
do
    syn_repo=${CORE_REPOSITORIES[$syn_name]}
    git clone $syn_repo
    
    git_dir="${PWD}/${syn_name}/.git"
    git_tree="${PWD}/${syn_name}"
    git --git-dir=$git_dir --work-tree=$git_tree checkout syncluster 
    git --git-dir=$git_dir --work-tree=$git_tree pull --recurse-submodules
done