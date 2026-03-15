# Weighted Risk Scoring Engine

## Overview
Production-grade, formula-based risk scoring system that goes beyond simple summation to provide intelligent risk prioritization.

## Scoring Formula

```
Final Risk Score = (Base Score + Cost Factor + Usage Factor) × Exposure Multiplier
```

### Components:

#### 1. Base Score (Weighted by Category)
```
Base Score = Σ(rule_risk × category_weight)
```

**Category Weights:**
- Security: 4x (highest priority)
- Compliance: 3x
- Cost: 2x
- Access: 3x

**Example:**
- Public resource (risk=9, category=security): 9 × 4 = 36
- No encryption (risk=7, category=security): 7 × 4 = 28
- Idle resource (risk=5, category=cost): 5 × 2 = 10
- **Base Score = 74**

#### 2. Cost Factor
```
Cost Factor = resource_cost / 5
```
Higher cost resources increase risk score proportionally.

**Example:**
- Resource cost = $10
- Cost Factor = 10 / 5 = 2

#### 3. Usage Factor
```
Usage Factor = 5 (if usage < 5%)
Usage Factor = 0 (otherwise)
```
Penalizes underutilized resources.

#### 4. Exposure Multiplier
```
Exposure Multiplier = 1.5 (if public = true)
Exposure Multiplier = 1.0 (otherwise)
```
Public resources are 50% more critical.

## Priority Thresholds

| Score Range | Priority | Action Required |
|-------------|----------|-----------------|
| >= 100      | CRITICAL | Immediate action |
| >= 60       | HIGH     | Urgent attention |
| >= 30       | MEDIUM   | Plan remediation |
| < 30        | LOW      | Monitor         |

## Real-World Example

**Resource r3 (Public Storage Bucket):**
```
Properties:
- Type: storage
- Usage: 0%
- Public: true
- Encrypted: false
- Cost: $2
- Logging: false

Matched Rules:
1. Public resource (risk=9, category=security)
2. Public storage bucket (risk=10, category=security)
3. No encryption (risk=7, category=security)
4. No logging (risk=6, category=compliance)
5. Idle resource (risk=5, category=cost)
6. Unused resource (risk=6, category=cost)

Calculation:
Base Score:
  9×4 + 10×4 + 7×4 + 6×3 + 5×2 + 6×2 = 36+40+28+18+10+12 = 144

Cost Factor: 2/5 = 0.4
Usage Factor: 5 (usage < 5%)

Subtotal: 144 + 0.4 + 5 = 149.4

Exposure Multiplier: 1.5 (public = true)

Final Score: 149.4 × 1.5 = 224.1

Priority: CRITICAL (>= 100)
```

## Why This Approach is Unique

### vs Simple Summation:
- **Simple:** risk_score = 9 + 10 + 7 + 6 + 5 + 6 = 43
- **Weighted:** risk_score = 224.1

### Production-Grade Features:
1. **Category Weighting** - Security issues weighted 4x vs cost issues 2x
2. **Cost Impact** - Expensive resources increase risk
3. **Usage Analysis** - Idle resources penalized
4. **Exposure Factor** - Public resources amplified
5. **Configurable** - All weights/thresholds in config file

### Industry Alignment:
Similar to:
- AWS Security Hub (severity scoring)
- Prisma Cloud (risk prioritization)
- Wiz (critical asset scoring)
- Azure Advisor (impact calculation)

## Configuration

All parameters are configurable in `scoring_config.json`:
```json
{
  "category_weights": {
    "security": 4,
    "compliance": 3,
    "cost": 2
  },
  "priority_thresholds": {
    "critical": 100,
    "high": 60,
    "medium": 30
  },
  "factors": {
    "cost_divisor": 5,
    "usage_threshold": 5,
    "usage_penalty": 5,
    "exposure_multiplier": 1.5
  }
}
```

## Results

From 50 resources analyzed:
- **14 CRITICAL** (score >= 100) - $41 cost at risk
- **2 HIGH** (score >= 60) - $2 cost at risk
- **6 MEDIUM** (score >= 30)
- **13 LOW** (score < 30)

**Total Potential Savings: $43**
