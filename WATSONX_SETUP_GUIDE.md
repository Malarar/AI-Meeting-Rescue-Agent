# IBM watsonx.ai Configuration Fix Guide

## 🔍 Problem Identified

Your AI Meeting Rescue Agent is failing with the following error:

```
Error: project_id 54a0562e-d293-4522-8279-3e8ae29c2d31 is not associated with a WML instance
Status Code: 403
```

**What this means:** Your IBM Cloud project exists and your API key is valid, but the project is **NOT associated with a Watson Machine Learning (WML) service instance**. This is required to use watsonx.ai foundation models like Granite.

## ✅ Diagnostic Results

The diagnostic script (`diagnose_watsonx.py`) confirmed:

- ✓ **API Key is VALID** - Your IBM Cloud authentication works
- ✓ **Project ID exists** - The project is accessible
- ✗ **WML Association MISSING** - Project is not linked to Watson Machine Learning

## 🔧 Solution Options

You have two options to fix this issue:

### Option 1: Create a New Project (RECOMMENDED - Easiest)

This is the simplest approach and ensures everything is configured correctly from the start.

#### Step-by-Step Instructions:

1. **Go to Watson Studio Projects**
   - URL: https://dataplatform.cloud.ibm.com/projects
   - Log in with your IBM Cloud credentials

2. **Create New Project**
   - Click the **"New project"** button (usually in the top right)
   - Select **"Create an empty project"**

3. **Configure Project**
   - **Name:** Enter a name like "AI Meeting Rescue Agent"
   - **Description:** (Optional) "Project for AI-powered meeting analysis"

4. **CRITICAL STEP - Associate Watson Machine Learning**
   - Look for the **"Select storage service"** section
   - You should also see **"Associate a Watson Machine Learning service"**
   - **If you have a WML service:** Select it from the dropdown
   - **If you DON'T have one:** Click "Create a new service instance"
     - Choose the **Lite plan** (free tier)
     - Select the **same region** as your project (e.g., us-south)
     - Click **Create**

5. **Get Your New Project ID**
   - After the project is created, click on it to open
   - Go to the **"Manage"** tab (or **"Settings"**)
   - Click on **"General"** section
   - Find and **COPY** the **"Project ID"** (it's a 36-character UUID like: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

6. **Update Your .env File**
   - Open the `.env` file in your AI Meeting Rescue Agent project
   - Find the line: `WATSONX_PROJECT_ID=54a0562e-d293-4522-8279-3e8ae29c2d31`
   - Replace it with your new Project ID: `WATSONX_PROJECT_ID=your-new-project-id-here`
   - **Save the file**

7. **Verify the Fix**
   - Run the diagnostic script again:
     ```bash
     python diagnose_watsonx.py
     ```
   - You should see: `[+] All tests PASSED!`

8. **Start Your Application**
   ```bash
   python run.py
   ```

---

### Option 2: Associate Your Existing Project with WML

If you want to keep using your current project (ID: `54a0562e-d293-4522-8279-3e8ae29c2d31`):

#### Method A: Through Watson Studio

1. **Open Your Project**
   - Go to: https://dataplatform.cloud.ibm.com/projects
   - Click on your existing project

2. **Access Services Settings**
   - Go to the **"Manage"** tab
   - Click on **"Services & integrations"** (or similar)

3. **Associate WML Service**
   - Click **"Associate service"** or **"Add service"**
   - Select **"Watson Machine Learning"**
   - Choose your WML instance from the dropdown
   - If you don't have one, create it first (see Method B below)
   - Click **"Associate"** or **"Add"**

4. **Verify**
   - Run the diagnostic: `python diagnose_watsonx.py`

#### Method B: Create WML Service First

If you don't have a Watson Machine Learning service instance:

1. **Create WML Service**
   - Go to: https://cloud.ibm.com/catalog/services/watson-machine-learning
   - Select a plan:
     - **Lite plan** (free) - Good for testing
     - **Standard plan** - For production use
   - Choose a **region** (must match your project region, e.g., us-south)
   - Give it a name (e.g., "WML-Meeting-Agent")
   - Click **"Create"**

2. **Associate with Project**
   - Follow Method A above to associate this new service with your project

---

## 🎯 Quick Reference

### Important URLs

- **Watson Studio Projects:** https://dataplatform.cloud.ibm.com/projects
- **IBM Cloud Console:** https://cloud.ibm.com/
- **API Keys Management:** https://cloud.ibm.com/iam/apikeys
- **WML Service Catalog:** https://cloud.ibm.com/catalog/services/watson-machine-learning
- **IBM Cloud Resources:** https://cloud.ibm.com/resources

### Your Current Configuration

```
URL:        https://us-south.ml.cloud.ibm.com
API Key:    ********************KzxZ (VALID ✓)
Project ID: 54a0562e-d293-4522-8279-3e8ae29c2d31 (EXISTS ✓, NOT ASSOCIATED WITH WML ✗)
Model ID:   ibm/granite-13b-chat-v2
```

### Diagnostic Commands

```bash
# Run diagnostic to check configuration
python diagnose_watsonx.py

# Test credentials (simpler version)
python test_credentials.py

# Start the application (after fixing)
python run.py
```

---

## 📝 Common Issues & Solutions

### Issue: "I don't see the WML association option when creating a project"

**Solution:** Make sure you're creating an **"Empty project"** not a "Project from file" or other template. The WML association option appears during empty project creation.

### Issue: "I created a WML service but can't find it in the dropdown"

**Solution:** 
- Make sure the WML service is in the **same region** as your project
- Wait a few minutes after creating the service
- Refresh the page

### Issue: "The Lite plan is not available"

**Solution:** You may already have a Lite plan WML instance. Check your resources at https://cloud.ibm.com/resources. You can only have one Lite plan per account.

### Issue: "After updating .env, the error persists"

**Solution:**
- Make sure you **saved** the .env file
- **Restart** any running application
- Run the diagnostic again to verify: `python diagnose_watsonx.py`

---

## 🎉 Success Indicators

When everything is configured correctly, you should see:

```
======================================================================
  Diagnostic Summary
======================================================================
[+] All tests PASSED!

[SUCCESS] Your configuration is correct and ready to use!

You can now run your application with:
   python run.py
```

---

## 📞 Need More Help?

- **IBM watsonx.ai Documentation:** https://cloud.ibm.com/docs/watsonx
- **Watson Machine Learning Docs:** https://cloud.ibm.com/docs/watson-machine-learning
- **IBM Cloud Support:** https://cloud.ibm.com/unifiedsupport/supportcenter

---

**Created by:** AI Meeting Rescue Agent Diagnostic Tool  
**Last Updated:** 2026-06-02