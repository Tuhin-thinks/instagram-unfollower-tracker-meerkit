# Visual Tour

Real UI screenshots from the project, grouped by workflow.

## 1) Onboarding and Account Control

### Login

![Follower Login](images/meerkit-follower-login.png)

### Admin Home

![Admin Window](images/meerkit-admin-window.png)

### Credential Health Monitor

![Admin Credentials Monitor](images/meerkit-admin-credentials-monitor.png)

### API Call Details per Account

![Admin Profile API Call Details](images/meerkit-admin-profile-page-with-api-call-details.png)

## 2) Dashboard and Scan Operations

### Automation Dashboard

![Automation Dashboard](images/meerkit-automation-dashboard.png)

### Batch Scan Trigger

![Batch Scan](images/meerkit-batch-scan.png)

### Running Task Controls

![Task Tab List Terminate Monitor Running Tasks](images/meerkit-task-tab-list-terminate-monitor-running-tasks.png)

### Scan History Timeline

![Scan History](images/meerkit-scan-history.png)

### Scan History Analytics Graph

![Scan History Analytics Graph](images/meerkit-scan-history-analytics-graph.png)

## 3) Discovery and Prediction Intelligence

### Discovery Page

![Discovery Page](images/meerkit-discovery-page.png)

### Detailed Profile in Discovery

![Discovery Detailed Profile](images/meerkit-discovery-page-detailed-profile.png)

### Intelligent Follow-Back Prediction

![Intelligent Followback Prediction](images/meerkit-intelligent-followback-prediction.png)

### Bulk Prediction Focus View

![Bulk Follow Back Predictions Focused](images/meerkit-bulk-follow-back-predictions-focused.png)

### Prediction Detail Focus in Discovery

![Follow Back Prediction Discover Detail Focused](images/meerkit-follow-back-predcition-discover-page-in-detail-focused.png)

### Feedback Loop for Better Accuracy

![Feedback Loop for Future Prediction Accuracy](images/meerkit-feedback-loop-for-future-prediction-accuracy.png)

## 4) Unfollow Workflow

### Candidate Selection

![Unfollow Candidates Who Dont Follow Back](images/meerkit-unfollow-candidates-who-dont-follow-back.png)

### Batch Unfollow with Sorting

![Batch Unfollow with Sorting](images/meerkit-batch-unfollow-with-sorting.png)

### Unfollow Confirmation

![Unfollow Successful](images/meerkit-unfollow-successful.png)

## 5) API Monitoring and Limits

Meerkit tracks every Instagram API call it makes on your behalf and surfaces that data in the **Admin → Account Details → API Usage** tab. Keeping an eye on these numbers is the easiest way to avoid triggering Instagram's rate-limit and spam detection systems.

!!! warning "⚠️ Instagram Rate Limit Warning"
    **Do not bulk follow or unfollow users on Instagram.** Doing so can trigger Instagram's spam detection and may lead to account restrictions.

    | Scenario | Safe daily limit |
    |---|---|
    | General / established accounts | 150 – 200 follow/unfollow actions |
    | New accounts (first few weeks) | Stay under 100 actions |

    - Spread your actions **gradually throughout the day** to avoid detection.
    - If you exceed the limit, Instagram may:
        - Temporarily block your actions (for hours or days)
        - Limit your reach (**shadowban**)
        - **Permanently disable** your account if abuse continues

    > **Note:** These limits are not officially confirmed by Instagram — they are based on extensive community testing and experience with Instagram automation tools.

    Use the **API Calls Count Dashboard** (shown below) to monitor your usage and stay within safe limits.

### API Calls Count Dashboard

![Insta API Calls Count Dashboard](images/meerkit-insta-api-calls-count-dashboard.png)

### Instagram API Usage Limits

![Instagram API Usage Limits](images/meerkit-instagram-api-usage-limits.png)

---

Want architecture details next? Jump to [Architecture](architecture.md).
