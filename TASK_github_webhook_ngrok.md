# Task — Trigger a Local Jenkins Pipeline from GitHub via ngrok

**Goal:** make a `git push` on a GitHub repository start a Jenkins pipeline running on your laptop **within seconds**, without opening any port on your router.

**Reference compose file:** `99_misc/setup/docker/docker-compose.yml`

---

## Background

GitHub's webhook delivery service runs in the public internet and cannot reach `http://localhost:80`. There are three options for bridging that gap:

| Option | When to use it |
|---|---|
| **ngrok** (this task) | Fast, ad-hoc, free tier is fine for a lab |
| `smee.io` relay | When you cannot run a public listener at all |
| `Poll SCM` cron in Jenkins | When latency does not matter and you do not want any external service |

ngrok publishes a public HTTPS URL that tunnels to your local Jenkins. GitHub posts the webhook to that public URL; ngrok forwards the request to `http://localhost:80/github-webhook/`; the **GitHub plugin** in Jenkins receives the post and triggers the matching job.

---

## Prerequisites

- Lab is up: `cd 99_misc/setup/docker && docker compose up -d --build`
- Jenkins reachable at `http://localhost`
- `ngrok` installed locally — `https://ngrok.com/download` (free account, single static URL is fine)
- A GitHub account and a **public** repository you can push to. If you do not have one, fork [vaiolabs-io/jenkins-examples](https://gitlab.com/vaiolabs-io/jenkins-examples) into GitHub via *Import repository*.
- A **GitHub Personal Access Token** with `repo` and `admin:repo_hook` scopes, saved somewhere safe — you will paste it into Jenkins as a credential.

---

## Setup Steps

### 1. Start the ngrok tunnel

```sh
ngrok config add-authtoken <YOUR_NGROK_TOKEN>   # one-time
ngrok http 80
```

ngrok prints something like:

```
Forwarding  https://abcd-12-34-56-78.ngrok-free.app -> http://localhost:80
```

Keep this terminal open for the duration of the task. **Copy the HTTPS URL** — you'll use it in step 4.

Smoke test from another terminal:

```sh
curl -I https://abcd-12-34-56-78.ngrok-free.app
# HTTP/1.1 200 OK   (Jenkins login page)
```

### 2. Install the GitHub plugin in Jenkins

`Manage Jenkins → Plugins → Available`

Install **GitHub** (this also pulls in `github-api` and `github-branch-source`). Restart Jenkins when prompted.

### 3. Add the GitHub credential

`Manage Jenkins → Credentials → System → Global → Add Credentials`

- Kind: `Username with password`
- Username: your GitHub login
- Password: the **Personal Access Token** from prerequisites
- ID: `github-pat`
- Description: `GitHub PAT for webhook + clone`

> [!] Note: a PAT works for both *triggering* (the webhook hits Jenkins) and *cloning* (Jenkins fetches the repo). For private repos you must have one.

### 4. Tell Jenkins its public URL

`Manage Jenkins → System → GitHub → Add GitHub Server`

- Name: `GitHub`
- API URL: `https://api.github.com`
- Credentials: `github-pat` (use the *Convert* dropdown to make it a *Secret text* if needed, or add a new *Secret text* credential containing just the PAT)
- Manage hooks: ✅
- Click **Test connection** — must show `Credentials verified for user <you>`

Scroll down to **Jenkins URL** at the top of `Manage Jenkins → System` and set:

```
Jenkins URL: https://abcd-12-34-56-78.ngrok-free.app/
```

This is the URL Jenkins advertises in webhook callbacks and badges.

### 5. Create the pipeline job

`New Item → Pipeline → name: github-webhook-demo → OK`

Configure:

- **Build Triggers** → ✅ `GitHub hook trigger for GITScm polling`
- **Pipeline → Definition**: `Pipeline script from SCM`
    - SCM: Git
    - Repository URL: `https://github.com/<you>/<repo>.git`
    - Credentials: `github-pat`
    - Branch: `*/main`
    - Script Path: `Jenkinsfile`

Save.

### 6. Register the webhook on GitHub

In your GitHub repo: `Settings → Webhooks → Add webhook`

- Payload URL: `https://abcd-12-34-56-78.ngrok-free.app/github-webhook/` *(trailing slash is required)*
- Content type: `application/json`
- Secret: leave empty for the lab (or set one and add it to the GitHub plugin config)
- Events: `Just the push event`
- Active: ✅

GitHub immediately fires a `ping` event. Open **Recent Deliveries** at the bottom of the webhook page — you should see `200 OK`. If you see `502`, ngrok or Jenkins is down. If you see `403`, the URL is wrong (most often the missing trailing slash).

---

## Practice

Add a `Jenkinsfile` to the **root of your repo** that prints the commit SHA, the GitHub event payload, and runs a trivial test step. Then push a commit and verify the pipeline starts on its own.

### Acceptance criteria

- [ ] ngrok's request log (terminal from step 1) shows `POST /github-webhook/` arriving from GitHub
- [ ] Jenkins shows a build queued **within 5 seconds** of pushing
- [ ] Build's *Changes* page lists the commit you just pushed, with the correct author
- [ ] Build's console output prints the commit SHA and the branch
- [ ] GitHub webhook **Recent Deliveries** shows `200 OK` for the push event
- [ ] Stopping ngrok and pushing again results in a `502` in **Recent Deliveries** *(proves the trigger really comes via the tunnel)*

### Solution — `Jenkinsfile`

```groovy
pipeline {
    agent any

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {
        stage('Checkout info') {
            steps {
                checkout scm
                sh 'git log -1 --pretty=format:"%h  %an  %s"'
                script {
                    env.SHORT_SHA = sh(
                        script: 'git rev-parse --short HEAD',
                        returnStdout: true
                    ).trim()
                }
                echo "Triggered by branch: ${env.BRANCH_NAME ?: env.GIT_BRANCH}"
                echo "Commit: ${env.SHORT_SHA}"
            }
        }

        stage('Verify webhook arrived') {
            steps {
                echo "Build cause(s): ${currentBuild.getBuildCauses()}"
            }
        }

        stage('Trivial test') {
            steps {
                sh 'echo "Hello from $(hostname)"'
                sh 'echo "Workspace: $WORKSPACE"'
            }
        }
    }

    post {
        success {
            echo "Build #${env.BUILD_NUMBER} for ${env.SHORT_SHA} succeeded"
        }
        failure {
            echo "Build #${env.BUILD_NUMBER} for ${env.SHORT_SHA} failed"
        }
    }
}
```

Trigger it:

```sh
echo "trigger $(date)" >> README.md
git add README.md
git commit -m "Test webhook"
git push origin main
```

Within ~3 seconds of pushing, **Build History** in Jenkins should show a new build with the cause **"Started by GitHub push by &lt;you&gt;"**.

---

## Stretch Goals

1. **Reserve a stable ngrok domain** so the URL survives restarts and you do not have to update GitHub each time.
2. **Sign the webhook** with a shared secret on both sides and confirm Jenkins rejects payloads with a wrong signature.
3. **Branch filtering** — make the pipeline only run for pushes to `main` and *develop*, ignoring all other branches.
4. **Status checks back to GitHub** — use the *GitHub Branch Source* plugin so the build result appears as a green/red check next to the commit on GitHub.

---

## Stretch Goal Solutions

### 1. Stable ngrok domain

```sh
# Reserve it once in the ngrok dashboard, then:
ngrok http --domain=jenkins-lab.ngrok-free.app 80
```

Update **Manage Jenkins → System → Jenkins URL** and the GitHub webhook URL to use that domain. After this, restarting ngrok does not break the integration.

### 2. Signed webhooks

In GitHub's webhook config, set a long random **Secret** (e.g. `openssl rand -hex 32`).

In Jenkins: `Manage Jenkins → System → GitHub → Advanced → Shared secrets → Add → Secret text` containing the same value. Save.

Verify rejection by editing the GitHub secret to something different and pushing — **Recent Deliveries** will show `403 Forbidden` from Jenkins.

### 3. Branch filtering

In a regular Pipeline job, the `branch '...'` directive of `when` is empty (it only works with Multibranch). For a regular declarative pipeline, use `env.GIT_BRANCH` — set automatically by the SCM checkout — together with `when { expression {} }`:

```groovy
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Run only on main / develop') {
            when {
                expression {
                    return env.GIT_BRANCH in ['origin/main', 'origin/develop']
                }
            }
            steps {
                echo "Building branch ${env.GIT_BRANCH}"
            }
        }

        stage('Skipped on other branches') {
            when {
                not {
                    expression {
                        return env.GIT_BRANCH in ['origin/main', 'origin/develop']
                    }
                }
            }
            steps {
                echo "Branch ${env.GIT_BRANCH} is not allow-listed — skipping."
            }
        }
    }
}
```

To make this useful, change the job's **Branches to build** specifier to `**` (all branches) so Jenkins runs on every push and lets the `when` block decide.

### 4. Status checks back to GitHub

Stay on the regular Pipeline job and post the status from the `post` block of the declarative pipeline. The `httpRequest` step (from the **HTTP Request** plugin) or a plain `curl` against GitHub's *commit statuses* API both work — `curl` keeps the dependency list small:

```groovy
pipeline {
    agent any

    environment {
        REPO = 'your-github-user/your-repo'   // edit me
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Test') {
            steps { sh 'echo running tests...' }
        }
    }

    post {
        success { script { postStatus('success', 'Build passed') } }
        failure { script { postStatus('failure', 'Build failed') } }
        unstable { script { postStatus('failure', 'Build unstable') } }
    }
}

void postStatus(String state, String description) {
    withCredentials([string(credentialsId: 'github-pat', variable: 'GH_TOKEN')]) {
        sh """
            curl -sS -X POST \\
              -H "Authorization: token \$GH_TOKEN" \\
              -H "Accept: application/vnd.github+json" \\
              https://api.github.com/repos/${env.REPO}/statuses/${env.GIT_COMMIT} \\
              -d '{"state":"${state}","context":"jenkins/build","description":"${description}","target_url":"${env.BUILD_URL}"}'
        """
    }
}
```

Re-add `github-pat` as a *Secret text* credential (Jenkins lets one PAT exist as both *Username with password* and *Secret text*). After the next push, the commit on GitHub shows a yellow "pending" dot that turns green or red, and the dot links back to the Jenkins build via `target_url`.

---

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| GitHub **Recent Deliveries** shows `502 Bad Gateway` | ngrok terminal closed or Jenkins not running on port 80. Reopen the tunnel and re-`ping` from the GitHub UI. |
| **Recent Deliveries** shows `403` | Wrong URL — most often missing trailing `/` on `/github-webhook/`, or signature mismatch when a secret is configured. |
| **Recent Deliveries** shows `200` but no Jenkins build | Job's "GitHub hook trigger" checkbox not enabled, or the repo URL in the job doesn't match the repo that fired the webhook (case-sen30027sitive, `.git` suffix matters in some plugin versions). |
| ngrok shows the request arriving but Jenkins logs `No git jenkins job found that matches ...` | Run `Manage Jenkins → System → GitHub → Re-register hooks for all jobs` once after creating the job, or check that the job's repo URL is *exactly* the same form GitHub announces. |
| Build runs but cannot clone the repo | Wrong/missing credential on the job, or the PAT lacks `repo` scope on a private repo. |
| Webhook URL changes every time you start ngrok | Free tier rotates by default — use **Stretch goal 1** to reserve a stable domain. |



