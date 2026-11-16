# 一键推送指令（作者在有网环境执行，约 5 分钟）

本目录已是完整仓库工作区（含修正后的根级 .github/workflows/benchmark-check.yml）。

```bash
cd 代码和脚本/open_benchmark_repo
git init -b main
git add -A
git -c user.name="Yuanshui Liu" -c user.email="yuanshuiliu@muhn.edu.cn" commit -m "Open dark-field velocity benchmark: 144-condition phantom, reference table, --check gate, dual-OS CI"
# 在 GitHub 网页新建空仓库后：
git remote add origin https://github.com/<USER>/open-benchmark-darkfield-velocity.git
git push -u origin main
```

推送后：GitHub → Actions 应出现 phantom-check 双 OS 运行且绿勾（首次即触发 push）。
确认绿勾后，可将稿件措辞从 "ships with the release ... to the hosted repository" 恢复为
"re-executes the gate on every push"。

本地预验（可选，推送前）：`python run_benchmark.py --check` 应输出 144/144 ALL MATCH。


## After the push succeeds (C4 completion, 2026-11-12 prep)

1. Confirm GitHub -> Actions shows phantom-check green on BOTH ubuntu-latest and windows-latest.
2. In Manuscript Section 2.3, after "...re-executes the gate on every push to the hosted repository"
   insert: " (https://github.com/<USER>/open-benchmark-darkfield-velocity; Actions run history public)".
3. In Code availability, append the same URL and one line: "The continuous-integration run history
   is publicly visible under the repository's Actions tab (ubuntu-latest and windows-latest)."
4. Optionally restore the stronger wording "re-executes the gate on every push" (now evidenced).
5. Regenerate Manuscript_BSPC_v13.0.docx after the two insertions.
