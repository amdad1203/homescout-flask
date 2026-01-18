# HomeScout – Real Estate Management System

HomeScout is a role-based real estate management web application built with **Flask** and **MySQL**, designed to simulate how real property brokerage firms actually operate — from listing verification to negotiation, analytics, and deal closure.

This is not just a listing website.  
It models the **human workflow behind real estate deals**.

---

## User Roles

- **Buyer** – Searches properties, submits requests, and negotiates deals
- **Seller** – Posts property with minimal information
- **Employee (Agent)** – Core mediator between buyer and seller
- **Admin** – Oversees the entire system, approvals, and business analytics

---

##  Key Features

- Smart property search with filters (location, price, rooms, floor)
- Buyer property requests routed to agents
- Seller listings verified and completed by agents
- Agent-led negotiation and visit coordination
- Admin dashboard with charts, reports, and performance metrics
- Fully relational MySQL database backend

---

##  Demo Flow (Real-World Scenario)

### Scenario: Mr. X wants to sell a flat, Mr. Y wants to buy one

**Step 1 – Seller Listing**  
Mr. X wants to sell his flat.  
He posts a listing on **HomeScout** with only **basic information** (location, price range, rooms).

**Step 2 – Agent Verification**  
An employee (agent) contacts Mr. X and collects detailed information:
- Flat size & floor
- Distance from main road, school, market
- Facing direction
- Environment & surroundings
- Utilities and lift availability

The agent verifies the details and submits the completed listing.

**Step 3 – Admin Approval**  
The admin reviews the property and **approves it** for public visibility in the system.

**Step 4 – Buyer Search**  
Mr. Y is looking for a flat.  
He searches HomeScout using his requirements (area, budget, rooms).

The system identifies matching properties and notifies an agent.

**Step 5 – Agent Mediation**  
The agent contacts Mr. Y, explains available options, and recommends the best deal.  
The agent then coordinates a **physical visit** between Mr. X and Mr. Y.

**Step 6 – Negotiation & Deal**  
The agent acts as a **neutral mediator**, negotiating for both parties.  
Once terms are agreed, the admin verifies documents and confirms legal accuracy.

**Step 7 – Deal Closure**  
The deal is closed successfully, generating profit for the company.

---

##  Business Intelligence & Reports

While deals are happening, the admin can analyze:
- Most selling locations
- Best performing agents
- Weekly / monthly revenue
- Sales trends and growth patterns

These insights help the company improve strategy and performance.

---

## 🛠 Tech Stack

- **Backend:** Flask (Python)
- **Frontend:** HTML, CSS, Jinja2
- **Database:** MySQL
- **Charts & Analytics:** Chart.js
- **Session Management:** Flask Sessions

---

##  How to Run Locally

```bash
python app.py
