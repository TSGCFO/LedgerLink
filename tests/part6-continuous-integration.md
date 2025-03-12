# Continuous Integration

Continuous Integration (CI) is the practice of automatically running tests whenever code changes are pushed to your repository. This ensures that all changes are tested before they're merged, helping you catch bugs early and maintain code quality.

## Table of Contents

1. [Setting Up GitHub Actions](#setting-up-github-actions)
2. [Setting Up GitLab CI](#setting-up-gitlab-ci)
3. [Setting Up Jenkins](#setting-up-jenkins)
4. [CI Pipeline Best Practices](#ci-pipeline-best-practices)
5. [Automated Deployment](#automated-deployment)

## Setting Up GitHub Actions

GitHub Actions is a built-in CI/CD solution available for GitHub repositories. It's easy to set up and integrates seamlessly with GitHub.

### Basic CI Workflow

Create a file at `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run Django tests
      run: |
        python manage.py test
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
  
  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '16'
        cache: 'npm'
        cache-dependency-path: 'frontend/package-lock.json'
    
    - name: Install frontend dependencies
      working-directory: ./frontend
      run: npm ci
    
    - name: Run frontend tests
      working-directory: ./frontend
      run: npm test -- --watchAll=false
```

### Advanced CI Workflow with Code Coverage

For a more comprehensive CI workflow that includes code coverage and linting:

```yaml
name: CI with Coverage

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install coverage pytest pytest-django flake8
    
    - name: Lint with flake8
      run: |
        # stop the build if there are Python syntax errors or undefined names
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        # exit-zero treats all errors as warnings
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Test with pytest and coverage
      run: |
        coverage run -m pytest
        coverage report
        coverage xml
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
  
  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '16'
        cache: 'npm'
        cache-dependency-path: 'frontend/package-lock.json'
    
    - name: Install frontend dependencies
      working-directory: ./frontend
      run: npm ci
    
    - name: Lint frontend code
      working-directory: ./frontend
      run: npm run lint
    
    - name: Run frontend tests with coverage
      working-directory: ./frontend
      run: npm test -- --coverage --watchAll=false
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./frontend/coverage/lcov.info
        fail_ci_if_error: true
```

### Adding End-to-End Tests to CI

To include Cypress end-to-end tests in your workflow:

```yaml
name: CI with E2E Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  # Previous backend-tests and frontend-tests jobs...
  
  e2e-tests:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '16'
    
    - name: Install backend dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Install frontend dependencies
      working-directory: ./frontend
      run: npm ci
    
    - name: Run migrations and create test data
      run: |
        python manage.py migrate
        python manage.py loaddata test_data
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
    
    - name: Start backend server
      run: |
        python manage.py runserver &
        echo $! > backend_pid.txt
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
    
    - name: Start frontend server
      working-directory: ./frontend
      run: |
        npm start &
        echo $! > frontend_pid.txt
      env:
        REACT_APP_API_URL: http://localhost:8000
    
    - name: Wait for servers to start
      run: |
        sleep 10
    
    - name: Run Cypress tests
      working-directory: ./frontend
      run: npx cypress run
    
    - name: Stop servers
      if: always()
      run: |
        if [ -f backend_pid.txt ]; then kill $(cat backend_pid.txt) || true; fi
        if [ -f frontend/frontend_pid.txt ]; then kill $(cat frontend/frontend_pid.txt) || true; fi
```

## Setting Up GitLab CI

If you use GitLab instead of GitHub, you can set up GitLab CI by creating a `.gitlab-ci.yml` file in your repository root:

```yaml
image: python:3.10

stages:
  - test
  - build
  - deploy

variables:
  POSTGRES_DB: test_db
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: postgres
  DATABASE_URL: "postgres://postgres:postgres@postgres:5432/test_db"

services:
  - postgres:13

backend-tests:
  stage: test
  script:
    - pip install -r requirements.txt
    - python manage.py test
  
frontend-tests:
  stage: test
  image: node:16
  script:
    - cd frontend
    - npm ci
    - npm test -- --watchAll=false

backend-lint:
  stage: test
  script:
    - pip install flake8
    - flake8 .

frontend-lint:
  stage: test
  image: node:16
  script:
    - cd frontend
    - npm ci
    - npm run lint

e2e-tests:
  stage: test
  image: cypress/browsers:node16.14.2-slim-chrome100-ff99-edge
  script:
    - apt-get update && apt-get install -y python3-pip
    - pip install -r requirements.txt
    - python manage.py migrate
    - python manage.py loaddata test_data
    - python manage.py runserver &
    - cd frontend
    - npm ci
    - npm start &
    - sleep 10
    - npx cypress run --browser chrome
  only:
    - main
    - merge_requests

build-backend:
  stage: build
  script:
    - pip install -r requirements.txt
    - python manage.py check --deploy
    - echo "Backend build successful"
  only:
    - main

build-frontend:
  stage: build
  image: node:16
  script:
    - cd frontend
    - npm ci
    - npm run build
    - echo "Frontend build successful"
  artifacts:
    paths:
      - frontend/build/
  only:
    - main

deploy-staging:
  stage: deploy
  script:
    - echo "Deploying to staging server"
    # Add your deployment commands here
  only:
    - main
  environment:
    name: staging
```

## Setting Up Jenkins

Jenkins is a self-hosted CI/CD solution that gives you more control over your CI/CD environment. Here's a sample Jenkinsfile:

```groovy
pipeline {
    agent {
        docker {
            image 'python:3.10'
        }
    }
    
    environment {
        DATABASE_URL = "postgres://postgres:postgres@postgres:5432/test_db"
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install -r requirements.txt'
                
                // Set up Node.js for frontend
                sh 'curl -sL https://deb.nodesource.com/setup_16.x | bash -'
                sh 'apt-get install -y nodejs'
                
                // Install frontend dependencies
                dir('frontend') {
                    sh 'npm ci'
                }
            }
        }
        
        stage('Backend Tests') {
            steps {
                sh 'python manage.py test'
            }
        }
        
        stage('Frontend Tests') {
            steps {
                dir('frontend') {
                    sh 'npm test -- --watchAll=false'
                }
            }
        }
        
        stage('Linting') {
            parallel {
                stage('Backend Lint') {
                    steps {
                        sh 'pip install flake8'
                        sh 'flake8 .'
                    }
                }
                
                stage('Frontend Lint') {
                    steps {
                        dir('frontend') {
                            sh 'npm run lint'
                        }
                    }
                }
            }
        }
        
        stage('Build') {
            parallel {
                stage('Backend Build') {
                    steps {
                        sh 'python manage.py check --deploy'
                    }
                }
                
                stage('Frontend Build') {
                    steps {
                        dir('frontend') {
                            sh 'npm run build'
                        }
                    }
                }
            }
        }
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                echo 'Deploying to production...'
                // Add your deployment commands here
            }
        }
    }
    
    post {
        always {
            // Clean up after the build
            cleanWs()
        }
    }
}
```

## CI Pipeline Best Practices

1. **Fast Feedback Loop**: Keep your CI pipeline fast so developers get feedback quickly. Split tests into categories by speed.

2. **Test Everything**: Include unit tests, integration tests, and end-to-end tests in your pipeline.

3. **Artifact Storage**: Store build artifacts for later use (e.g., deployments or debugging).

4. **Security Scanning**: Include security scans to catch vulnerabilities early:

   ```yaml
   security-scan:
     runs-on: ubuntu-latest
     steps:
     - uses: actions/checkout@v3
     
     - name: Run security scan
       uses: snyk/actions/python@master
       with:
         args: --severity-threshold=high
       env:
         SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
   ```

5. **Parallel Execution**: Run tests in parallel to speed up the pipeline.

6. **Test in Production-Like Environment**: Make your CI environment as similar to production as possible.

7. **Branch Policies**: Require passing CI checks before merge to protected branches.

8. **Reduce Flakiness**: Identify and fix flaky tests to maintain developer trust in the CI system.

9. **Notifications**: Set up notifications for build failures to get immediate attention.

10. **Badge Status**: Add status badges to your README to show the current build status.

## Automated Deployment

Once your tests pass, you can automatically deploy your application to staging or production environments.

### GitHub Actions Deployment to Heroku

Here's an example of deploying to Heroku after tests pass:

```yaml
name: CI/CD

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  # Include previous test jobs...
  
  deploy-to-heroku:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install Heroku CLI
      run: curl https://cli-assets.heroku.com/install.sh | sh
    
    - name: Build frontend
      working-directory: ./frontend
      run: |
        npm ci
        npm run build
        cp -r build/ ../static/
    
    - name: Deploy to Heroku
      run: |
        heroku git:remote -a your-heroku-app-name
        git push heroku main
      env:
        HEROKU_API_KEY: ${{ secrets.HEROKU_API_KEY }}
```

### GitHub Actions Deployment to AWS

Here's an example of deploying to AWS Elastic Beanstalk:

```yaml
name: CI/CD

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  # Include previous test jobs...
  
  deploy-to-aws:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '16'
    
    - name: Build frontend
      working-directory: ./frontend
      run: |
        npm ci
        npm run build
        cp -r build/ ../static/
    
    - name: Generate deployment package
      run: |
        pip install -r requirements.txt
        pip install awsebcli
        zip -r deploy.zip . -x "*.git*" "frontend/node_modules/*" "frontend/src/*"
    
    - name: Deploy to Elastic Beanstalk
      uses: einaregilsson/beanstalk-deploy@v20
      with:
        aws_access_key: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws_secret_key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        application_name: your-application-name
        environment_name: your-environment-name
        version_label: ${{ github.sha }}
        region: us-west-2
        deployment_package: deploy.zip
```

### Automating Database Migrations

When deploying to production, you often need to run database migrations. Add migration steps to your deployment workflow:

```yaml
deploy-to-production:
  runs-on: ubuntu-latest
  needs: [tests]
  if: github.ref == 'refs/heads/main'
  
  steps:
  - uses: actions/checkout@v3
  
  # ... other setup steps ...
  
  - name: Run database migrations
    run: |
      python manage.py migrate --noinput
    env:
      DATABASE_URL: ${{ secrets.PRODUCTION_DATABASE_URL }}
  
  # ... other deployment steps ...
```

### Blue-Green Deployment

For zero-downtime deployments, consider implementing a blue-green deployment strategy:

```yaml
deploy-blue-green:
  runs-on: ubuntu-latest
  needs: [tests]
  if: github.ref == 'refs/heads/main'
  
  steps:
  - uses: actions/checkout@v3
  
  # ... setup steps ...
  
  - name: Deploy to green environment
    run: |
      # Deploy to the green environment
      ssh ${{ secrets.DEPLOY_USER }}@${{ secrets.DEPLOY_HOST }} "cd /opt/app/green && git pull"
      ssh ${{ secrets.DEPLOY_USER }}@${{ secrets.DEPLOY_HOST }} "cd /opt/app/green && ./deploy.sh"
  
  - name: Run migrations
    run: |
      ssh ${{ secrets.DEPLOY_USER }}@${{ secrets.DEPLOY_HOST }} "cd /opt/app/green && python manage.py migrate"
  
  - name: Run smoke tests
    run: |
      # Run quick smoke tests against green environment
      curl -f https://green.yourapp.com/health || exit 1
  
  - name: Switch to green environment
    run: |
      # Switch the load balancer to point to green
      ssh ${{ secrets.DEPLOY_USER }}@${{ secrets.DEPLOY_HOST }} "sudo /opt/scripts/switch-to-green.sh"
```

### Rollback Strategy

Always have a rollback plan in case a deployment goes wrong:

```yaml
deploy-to-production:
  runs-on: ubuntu-latest
  needs: [tests]
  if: github.ref == 'refs/heads/main'
  
  steps:
  # ... deployment steps ...
  
  - name: Run smoke tests
    id: smoke_tests
    continue-on-error: true
    run: |
      # Run quick smoke tests
      curl -f https://yourapp.com/health || exit 1
  
  - name: Rollback if necessary
    if: steps.smoke_tests.outcome == 'failure'
    run: |
      # Rollback to previous version
      heroku rollback -a your-heroku-app-name
    env:
      HEROKU_API_KEY: ${{ secrets.HEROKU_API_KEY }}
  
  - name: Notify on rollback
    if: steps.smoke_tests.outcome == 'failure'
    uses: rtCamp/action-slack-notify@v2
    env:
      SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
      SLACK_COLOR: danger
      SLACK_TITLE: Deployment Rolled Back
      SLACK_MESSAGE: 'Automatic rollback triggered due to failed smoke tests!'
```

By implementing these CI/CD practices, you can ensure that your Django and React application is automatically tested and deployed with every code change, providing fast feedback to developers and reliable deployments to your users.
