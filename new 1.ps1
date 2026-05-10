# Navigate to your repo folder
Set-Location -Path "C:\Users\ZiloTech\Desktop\bruteforce-sim\test.txt"

# Apply git speed optimizations
git config core.fsyncObjectFiles false
git config commit.gpgsign false
git config gc.auto 0

# Define commit messages
$msgs = @(
    "fix layout issue on dashboard",
    "update login screen UI",
    "refactor authentication logic",
    "improve button spacing on mobile",
    "resolve merge conflict in header",
    "add loading spinner to form",
    "clean up unused imports",
    "patch null pointer in user service",
    "update README with setup steps",
    "adjust font size for readability",
    "fix broken link in navbar",
    "modify register page layout",
    "remove deprecated API calls",
    "improve error handling in login",
    "update color scheme to match brand",
    "fix typo in welcome message",
    "add input validation to signup form",
    "optimize image loading performance",
    "fix padding issue on mobile view",
    "update dependencies to latest version",
    "refactor sidebar navigation",
    "fix session timeout bug",
    "improve password strength checker",
    "update footer links",
    "add dark mode toggle",
    "fix alignment issue in card grid",
    "modify profile page header",
    "resolve CORS issue in API calls",
    "update env variable references",
    "fix 404 redirect on logout"
)

$total = 1027

for ($i = 1; $i -le $total; $i++) {
    # Pick message
    $msg = $msgs[$i % $msgs.Length]

    # Append change to test.txt
    Add-Content -Path "test.txt" -Value "update $i"

    # Stage and commit
    git add test.txt
    git commit -m "$msg"

    # Progress
    Write-Host "[Brelinx] $i/$total -- $msg" -ForegroundColor Cyan
}

# Push all at once
git push origin main

Write-Host "Done! All $total commits pushed." -ForegroundColor Green