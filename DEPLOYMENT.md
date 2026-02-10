# Render Deployment Checklist

This checklist will guide you through deploying the Storyframes backend to Render with PayPal integration.

## Prerequisites

- [ ] GitHub account with access to the `Sviievmla/storyframes-backend` repository
- [ ] Render account (sign up at https://render.com)
- [ ] PayPal Developer account (https://developer.paypal.com)
- [ ] Email account for SMTP (Gmail recommended)

## Step 1: PayPal Setup

### For Testing (Sandbox)

1. [ ] Go to https://developer.paypal.com/developer/applications
2. [ ] Make sure you're in "Sandbox" mode (toggle in top right)
3. [ ] Click "Create App"
4. [ ] Name: "Storyframes Sandbox"
5. [ ] Copy the **Sandbox Client ID** and **Secret**

### For Production (Live)

1. [ ] Go to https://developer.paypal.com/developer/applications
2. [ ] Switch to "Live" mode (toggle in top right)
3. [ ] Click "Create App"
4. [ ] Name: "Storyframes Live"
5. [ ] App Type: Merchant
6. [ ] Copy the **Live Client ID** and **Secret**

## Step 2: Email Setup (Gmail)

1. [ ] Go to your Google Account: https://myaccount.google.com/
2. [ ] Navigate to Security
3. [ ] Enable 2-Step Verification if not already enabled
4. [ ] Go to App Passwords: https://myaccount.google.com/apppasswords
5. [ ] Select app: "Mail"
6. [ ] Select device: "Other (Custom name)" → Enter "Storyframes"
7. [ ] Click Generate
8. [ ] Copy the 16-character app password (remove spaces)

## Step 3: Create PostgreSQL Database on Render

1. [ ] Log in to Render Dashboard: https://dashboard.render.com
2. [ ] Click "New +" → Select "PostgreSQL"
3. [ ] Configure:
   - Name: `storyframes-db`
   - Database: `storyframes`
   - User: `storyframes_user` (or auto-generated)
   - Region: Choose closest to your users
   - Plan: Free (or paid based on needs)
4. [ ] Click "Create Database"
5. [ ] Wait for database to provision (usually 1-2 minutes)
6. [ ] Note the **Internal Database URL** (format: `postgres://...`)

## Step 4: Deploy Web Service on Render

1. [ ] In Render Dashboard, click "New +" → Select "Web Service"
2. [ ] Connect your GitHub account if not already connected
3. [ ] Select repository: `Sviievmla/storyframes-backend`
4. [ ] Configure:
   - **Name**: `storyframes-backend`
   - **Region**: Same as database
   - **Branch**: `main` (or your deployment branch)
   - **Root Directory**: Leave blank
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (or paid based on needs)

## Step 5: Configure Environment Variables

In the web service settings, go to "Environment" tab and add:

### Required Variables

1. [ ] **PAYPAL_CLIENT_ID**
   - Value: Your PayPal Client ID (Sandbox or Live)
   
2. [ ] **PAYPAL_CLIENT_SECRET**
   - Value: Your PayPal Client Secret (Sandbox or Live)
   
3. [ ] **PAYPAL_MODE**
   - Value: `sandbox` (for testing) or `live` (for production)

### Optional but Recommended for Production

4. [ ] **SMTP_HOST**
   - Value: `smtp.gmail.com`
   
5. [ ] **SMTP_PORT**
   - Value: `587`
   
6. [ ] **SMTP_USERNAME**
   - Value: Your Gmail address
   
7. [ ] **SMTP_PASSWORD**
   - Value: Your Gmail app password (16-character)
   
8. [ ] **FROM_EMAIL**
   - Value: `noreply@mystoryframes.shop` (or your preferred email)
   
9. [ ] **ADMIN_EMAIL**
   - Value: Your admin email address for order notifications

### Database Connection

10. [ ] **DATABASE_URL**
    - Click "Add Environment Variable" → "From Database"
    - Select the PostgreSQL database you created
    - This will automatically add the DATABASE_URL

## Step 6: Deploy

1. [ ] Click "Create Web Service"
2. [ ] Wait for the deployment to complete (usually 2-5 minutes)
3. [ ] Check the logs for any errors
4. [ ] Look for: `INFO: Uvicorn running on http://0.0.0.0:$PORT`

## Step 7: Verify Deployment

1. [ ] Note your Render URL: `https://storyframes-backend.onrender.com` (or similar)
2. [ ] Test health endpoint: `https://your-app.onrender.com/health`
   - Should return: `{"status": "healthy", "service": "storyframes-backend"}`
3. [ ] Test API docs: `https://your-app.onrender.com/docs`
   - Should show Swagger UI with all endpoints

## Step 8: Test PayPal Integration

1. [ ] Use the Swagger UI (`/docs`) to test the endpoints
2. [ ] Try creating an order with the `/api/paypal/create-order` endpoint
3. [ ] Copy the returned `orderID`
4. [ ] Go to PayPal Sandbox: https://www.sandbox.paypal.com
5. [ ] Log in with a sandbox test account
6. [ ] Complete the payment
7. [ ] Use the `/api/paypal/capture-order` endpoint with the orderID
8. [ ] Verify order appears in `/api/orders` list
9. [ ] Check your email for confirmation (if SMTP configured)

## Step 9: Configure Custom Domain (Optional)

1. [ ] In your web service settings, go to "Custom Domain"
2. [ ] Click "Add Custom Domain"
3. [ ] Enter your domain: `api.mystoryframes.shop`
4. [ ] Add the CNAME record to your DNS:
   - Name: `api`
   - Type: `CNAME`
   - Value: `your-app.onrender.com`
   - TTL: `3600` (or as recommended)
5. [ ] Wait for DNS propagation (5-30 minutes)
6. [ ] Verify SSL certificate is issued automatically

## Step 10: Update Frontend

1. [ ] Update your frontend checkout.html
2. [ ] Replace API base URL with: `https://your-app.onrender.com`
3. [ ] Test the complete checkout flow from frontend

## Step 11: Go Live with PayPal

Once everything is tested with Sandbox:

1. [ ] Switch PayPal to Live mode (see Step 1)
2. [ ] Update Render environment variables:
   - `PAYPAL_CLIENT_ID`: Live Client ID
   - `PAYPAL_CLIENT_SECRET`: Live Client Secret
   - `PAYPAL_MODE`: `live`
3. [ ] Restart the web service (Render → Manual Deploy → "Clear build cache & deploy")
4. [ ] Test with a small real payment
5. [ ] Verify in PayPal Live dashboard

## Monitoring and Maintenance

- [ ] Set up Render health checks (automatic)
- [ ] Monitor logs regularly: Render Dashboard → Logs
- [ ] Set up email alerts for service issues
- [ ] Monitor PayPal dashboard for transactions
- [ ] Back up database regularly (Render automatic backups on paid plans)

## Troubleshooting

### Service Won't Start

- Check logs for errors
- Verify all required environment variables are set
- Ensure DATABASE_URL is connected correctly
- Check that Python version is compatible (3.10+)

### PayPal Errors

- Verify credentials are correct
- Check PAYPAL_MODE matches credentials (sandbox/live)
- Verify API is enabled in PayPal app settings
- Check PayPal API status: https://www.paypal-status.com/

### Email Not Sending

- Verify Gmail app password (not regular password)
- Check SMTP settings are correct
- Ensure 2FA is enabled on Gmail account
- Try testing with a different email service if issues persist

### Database Connection Issues

- Verify DATABASE_URL is set
- Check database is running in Render dashboard
- Ensure web service and database are in same region
- Try restarting the database

## Security Reminders

- ✅ Never commit secrets to GitHub
- ✅ Use environment variables for all sensitive data
- ✅ Keep PayPal credentials secure
- ✅ Regularly update dependencies
- ✅ Monitor for security vulnerabilities
- ✅ Use HTTPS only (automatic on Render)
- ✅ Enable 2FA on all accounts

## Success Criteria

- [x] Backend is running on Render
- [x] Database is connected
- [x] Health endpoint returns 200 OK
- [x] API docs are accessible
- [x] PayPal orders can be created
- [x] PayPal orders can be captured
- [x] Orders are stored in database
- [x] Email notifications are sent
- [x] Frontend can connect to backend
- [x] Complete checkout flow works end-to-end

## Next Steps After Deployment

1. Set up monitoring and alerts
2. Configure automatic backups
3. Plan for scaling if needed
4. Document the order fulfillment process
5. Set up customer support workflow
6. Plan for handling refunds and disputes

---

Need help? Check:
- Render Documentation: https://render.com/docs
- PayPal Developer Docs: https://developer.paypal.com/docs
- FastAPI Documentation: https://fastapi.tiangolo.com
