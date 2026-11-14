#!/bin/bash
# Runs the E02 main pilot after turn 1, in priority order (core cells first, bare-assertion cells last).
# Run it only after turn 1 has finished (run.py turn1). An earlier version waited on `pgrep -f "...run.py turn1"`,
# which matched its own launching shell and deadlocked; the wait was removed.
# Usage: nohup bash experiments/E02_flip_2x2/pipeline.sh >/dev/null 2>>results/E02/run.log &
cd "$(dirname "$0")/../.."
D=experiments/E02_flip_2x2
R=results/E02
rm -f $R/PIPELINE_DONE
echo "=== $(date -u +%FT%TZ) pipeline: turn2 core cells ===" >> $R/run.log
uv run python $D/run.py turn2 --cells R_flawed,W_sound,W_flawed >/dev/null || exit 1
echo "=== $(date -u +%FT%TZ) pipeline: validation ===" >> $R/run.log
uv run python $D/run.py validate --n 45 >/dev/null
uv run python $D/analyze.py > $R/analyze_stdout_core.txt 2>&1
echo "=== $(date -u +%FT%TZ) pipeline: bandit ===" >> $R/run.log
uv run python $D/bandit.py --pulls 160 > $R/bandit_stdout.txt
echo "=== $(date -u +%FT%TZ) pipeline: turn2 bare cells ===" >> $R/run.log
uv run python $D/run.py turn2 --cells R_bare,W_bare >/dev/null
uv run python $D/analyze.py > $R/analyze_stdout.txt 2>&1
uv run python $D/analyze.py --valid-only > $R/analyze_stdout_validonly.txt 2>&1
echo "=== $(date -u +%FT%TZ) pipeline: done ===" >> $R/run.log
touch $R/PIPELINE_DONE
