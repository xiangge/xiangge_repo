# export GATEWAY_ALLOWED_REPOS=xiangge/gravity-shift
export GATEWAY_ALLOWED_REPOS=xiangge/gravity-shift,xiangge/finding-jobs  
export GATEWAY_BEARER_TOKEN=
# export GATEWAY_REPO_URL=git@github.com:xiangge/gravity-shift.git
export GATEWAY_REPO_URLS='xiangge/gravity-shift=git@github.com:xiangge/gravity-shift.git,xiangge/finding-jobs=git@github.com:xiangge/finding-jobs.git'
export GATEWAY_HOST=127.0.0.1
export GATEWAY_PORT=8787
export GATEWAY_CODEX_BIN=/Applications/ChatGPT.app/Contents/Resources/codex
export GATEWAY_ALLOWED_COMMENT_LOGINS=xiangge
export GATEWAY_TEST_COMMANDS='{"xiangge/finding-jobs":"pytest","xiangge/gravity-shift":"npm test"}'
export GATEWAY_EVAL_COMMANDS='{"xiangge/finding-jobs":"python evals/run_eval.py","xiangge/gravity-shift":"npm run eval"}'
