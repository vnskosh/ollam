if ! command -v ollama &> /dev/null
then
    exit 1
git init
ollama pull llama3

if [ $? -ne 0 ]; then
    exit 1
cat > README.md <<EOL
ollama run llama3
#git add .
