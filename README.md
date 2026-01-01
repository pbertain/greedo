# Gree.do - Star Wars Holonet Timestamp System

A dynamic web service that provides both real-world and Star Wars-themed timestamps through a beautiful animated interface and REST API endpoints.

## 🚀 Live Demo

Visit the live site at: **[Your deployment URL]**

## ✨ Features

- **Dynamic Web Interface**: Beautiful animated webpage with emerald/teal theme
- **REST API Endpoints**: JSON and text-based API responses
- **Star Wars Time Systems**: SWET (Star Wars Epoch Time), CGT (Combine Galactic Time), and more
- **Real-time Data**: Current UTC, local time, and Unix epoch timestamps
- **Interactive Documentation**: Swagger/OpenAPI and ReDoc interfaces
- **Health Check**: Comprehensive system status monitoring

## 🎯 API Endpoints

### JSON API
```
GET /api/v1/greedo
```
Returns structured JSON with timestamp data and Star Wars facts.

### Text/cURL API
```
GET /curl/v1/greedo
```
Returns plain text format optimized for command-line usage.

### Example Response
```
Fact: Han shot first.
Rando Factissian: (random Star Wars quote)

Real Time:
  UTC   : Wed 2025-12-31 22:18:23
  Local : Wed 2025-12-31 14:18:23 PST

Unix Epoch:
  Unix  : 1767229103

Star Wars Time:
  SWET  : 1533560623
  CGT   : CGT 27 365 15:18:23
  GSC   : 25070
```

## 🛠 Installation & Deployment

### Local Development

#### Prerequisites
- Python 3.9+
- Virtual environment support

#### Setup
```bash
# Clone the repository
git clone https://github.com/pbertain/greedo.git
cd greedo

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the web server
python3 app.py
```

### Production Deployment

Gree.do uses GitHub Actions with Ansible for automated deployments to both dev and production environments.

#### Environments
- **Development**: `http://host78.nird.club:17000` (auto-deploys from `dev` branch)
- **Production**: `http://host74.nird.club:17000` (manual deployment with confirmation)

#### Quick Deploy
1. **Dev Environment**: Push to `dev` branch triggers automatic deployment
2. **Production**: Use GitHub Actions "Deploy to Production" workflow (requires `DEPLOY-TO-PROD` confirmation)

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment documentation.

## 📖 Documentation

- **Swagger UI**: `/docs` - Interactive API testing interface
- **ReDoc**: `/redoc` - Comprehensive API documentation
- **Health Check**: `/health` - System status and diagnostics
- **About SWET**: `/about` - Learn about Star Wars Epoch Time

## 🎨 Star Wars Time Systems

### SWET (Star Wars Epoch Time)
Custom epoch time starting from the theatrical release of Star Wars (1977-05-25 00:00:00 UTC). Similar to Unix time but with a galactic twist!

### CGT (Combine Galactic Time)
- 365-day years, 24-hour days
- Day of year: 1–365
- Supports current and legacy epoch modes

### Other Systems
- **GSC**: Galactic Standard Calendar
- **BBY/ABY**: Before/After Battle of Yavin
- **BTC/ATC**: Before/After Treaty of Coruscant

## 🧪 Testing

Run the complete test suite:
```bash
python -m unittest discover -v
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Credits

- Star Wars calendar conversions based on [Crystal Odenkirk's work](https://crysodenkirk.com/conlangs/SWtimeline.php)
- CGT implementation inspired by [SWCombine rules](https://www.swcombine.com/rules/?Timeframe#Combine_Galactic_Time)

---

*Remember: Han shot first.* 🚀