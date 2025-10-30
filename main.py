# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import json
from typing import List, Dict
import random

app = FastAPI(title="Geo-Keyword Finder API - No API Keys")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
def init_db():
    conn = sqlite3.connect('geo_keyword.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            business_type TEXT NOT NULL,
            keywords TEXT,
            competitor_count INTEGER,
            sentiment_score REAL,
            recommendation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS location_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT UNIQUE,
            population INTEGER,
            avg_income REAL,
            growth_rate REAL
        )
    ''')
    
    # Sample data for Indian cities
    sample_locations = [
        ('Chennai', 8000000, 45000, 4.2),
        ('Bangalore', 12000000, 65000, 6.8),
        ('Mumbai', 20000000, 55000, 5.1),
        ('Delhi', 18000000, 50000, 4.8),
        ('Hyderabad', 9000000, 48000, 5.5),
        ('Kolkata', 14000000, 42000, 3.9),
        ('Pune', 7000000, 52000, 6.2)
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO location_data (location, population, avg_income, growth_rate)
        VALUES (?, ?, ?, ?)
    ''', sample_locations)
    
    conn.commit()
    conn.close()

init_db()

# Data models
class SearchRequest(BaseModel):
    location: str
    business_type: str

class AnalysisResult(BaseModel):
    location: str
    business_type: str
    trending_keywords: List[str]
    competitor_count: int
    sentiment_score: float
    recommendation: str
    market_score: float
    suggested_locations: List[str]

# Mock Data Services - No API Keys Required
class MockMapsService:
    LOCATION_BUSINESS_DATA = {
        'chennai': {
            'gym': {'competitors': 45, 'areas': ['Tambaram', 'Anna Nagar', 'T Nagar', 'Adyar']},
            'restaurant': {'competitors': 120, 'areas': ['ECR', 'OMR', 'City Center']},
            'cafe': {'competitors': 65, 'areas': ['Bessie Beach', 'Nungambakkam']},
            'salon': {'competitors': 35, 'areas': ['Velachery', 'Porur', 'Chrompet']},
            'retail store': {'competitors': 80, 'areas': ['Phoenix Marketcity', 'Forum Mall', 'Express Avenue']}
        },
        'bangalore': {
            'gym': {'competitors': 85, 'areas': ['Koramangala', 'Indiranagar', 'Whitefield']},
            'restaurant': {'competitors': 200, 'areas': ['MG Road', 'Church Street']},
            'cafe': {'competitors': 120, 'areas': ['Jayanagar', 'HSR Layout']},
            'salon': {'competitors': 60, 'areas': ['Jayanagar', 'JP Nagar', 'Bellandur']},
            'retail store': {'competitors': 150, 'areas': ['Orion Mall', 'UB City', 'Mantri Square']}
        },
        'mumbai': {
            'gym': {'competitors': 95, 'areas': ['Bandra', 'Andheri', 'Powai']},
            'restaurant': {'competitors': 180, 'areas': ['Colaba', 'Bandra']},
            'cafe': {'competitors': 110, 'areas': ['Lower Parel', 'Juhu']},
            'salon': {'competitors': 75, 'areas': ['Bandra', 'Andheri', 'Dadar']},
            'retail store': {'competitors': 130, 'areas': ['Palladium', 'Inorbit', 'R City']}
        },
        'delhi': {
            'gym': {'competitors': 70, 'areas': ['Connaught Place', 'Saket', 'Rajouri Garden']},
            'restaurant': {'competitors': 160, 'areas': ['Connaught Place', 'Hauz Khas']},
            'cafe': {'competitors': 90, 'areas': ['Greater Kailash', 'Defence Colony']},
            'salon': {'competitors': 50, 'areas': ['South Extension', 'Vasant Kunj']},
            'retail store': {'competitors': 110, 'areas': ['Select Citywalk', 'DLF Promenade']}
        },
        'hyderabad': {
            'gym': {'competitors': 40, 'areas': ['Banjara Hills', 'Jubilee Hills', 'Gachibowli']},
            'restaurant': {'competitors': 100, 'areas': ['Banjara Hills', 'Jubilee Hills']},
            'cafe': {'competitors': 70, 'areas': ['Madhapur', 'Kondapur']},
            'salon': {'competitors': 30, 'areas': ['Banjara Hills', 'Jubilee Hills']},
            'retail store': {'competitors': 60, 'areas': ['Inorbit Mall', 'Forum Sujana']}
        },
        'kolkata': {
            'gym': {'competitors': 35, 'areas': ['Park Street', 'Salt Lake', 'New Town']},
            'restaurant': {'competitors': 90, 'areas': ['Park Street', 'Salt Lake']},
            'cafe': {'competitors': 55, 'areas': ['Park Street', 'Camac Street']},
            'salon': {'competitors': 25, 'areas': ['Salt Lake', 'New Town']},
            'retail store': {'competitors': 70, 'areas': ['South City Mall', 'Quest Mall']}
        },
        'pune': {
            'gym': {'competitors': 50, 'areas': ['Koregaon Park', 'Kothrud', 'Hinjewadi']},
            'restaurant': {'competitors': 110, 'areas': ['Koregaon Park', 'FC Road']},
            'cafe': {'competitors': 75, 'areas': ['Koregaon Park', 'JM Road']},
            'salon': {'competitors': 40, 'areas': ['Kothrud', 'Aundh']},
            'retail store': {'competitors': 85, 'areas': ['Phoenix Marketcity', 'Amanora Mall']}
        }
    }
    
    @staticmethod
    def get_competitor_count(location: str, business_type: str) -> int:
        location_key = location.lower().strip()
        business_key = business_type.lower().strip()
        
        if location_key in MockMapsService.LOCATION_BUSINESS_DATA:
            if business_key in MockMapsService.LOCATION_BUSINESS_DATA[location_key]:
                return MockMapsService.LOCATION_BUSINESS_DATA[location_key][business_key]['competitors']
        
        return random.randint(20, 100)
    
    @staticmethod
    def get_suggested_areas(location: str, business_type: str) -> List[str]:
        location_key = location.lower().strip()
        business_key = business_type.lower().strip()
        
        if location_key in MockMapsService.LOCATION_BUSINESS_DATA:
            if business_key in MockMapsService.LOCATION_BUSINESS_DATA[location_key]:
                return MockMapsService.LOCATION_BUSINESS_DATA[location_key][business_key]['areas']
        
        return [f"Area {i+1}" for i in range(3)]

class MockTrendsService:
    KEYWORD_TEMPLATES = {
        'gym': ['fitness', 'workout', 'training', 'exercise', 'health', 'wellness', 
                'personal trainer', 'yoga', 'cardio', 'strength'],
        'restaurant': ['food', 'cuisine', 'dining', 'meal', 'delicious', 'fresh',
                      'authentic', 'family', 'romantic', 'outdoor'],
        'cafe': ['coffee', 'tea', 'brew', 'artisan', 'pastry', 'bakery',
                'study', 'work', 'meeting', 'relax'],
        'salon': ['beauty', 'spa', 'haircut', 'styling', 'grooming', 'wellness',
                 'skincare', 'massage', 'treatment', 'relaxation'],
        'retail store': ['shopping', 'fashion', 'lifestyle', 'branded', 'discount',
                  'premium', 'trendy', 'affordable', 'quality', 'variety']
    }
    
    @staticmethod
    def get_trending_keywords(location: str, business_type: str) -> List[str]:
        business_key = business_type.lower().strip()
        base_keywords = MockTrendsService.KEYWORD_TEMPLATES.get(
            business_key, 
            ['service', 'quality', 'professional', 'best', 'top']
        )
        
        shuffled = base_keywords.copy()
        random.shuffle(shuffled)
        selected = shuffled[:5]
        
        return [f"{kw} {location.lower()}" for kw in selected]

class AnalysisService:
    def __init__(self):
        self.maps_service = MockMapsService()
        self.trends_service = MockTrendsService()

    def analyze_location(self, request: SearchRequest) -> AnalysisResult:
        competitor_count = self.maps_service.get_competitor_count(
            request.location, request.business_type
        )

        trending_keywords = self.trends_service.get_trending_keywords(
            request.location, request.business_type
        )

        # Calculate sentiment based on business type and location
        sentiment_score = self._calculate_sentiment(request.business_type, request.location)
        
        # Calculate market score
        market_score = self._calculate_market_score(competitor_count, sentiment_score)
        
        suggested_locations = self.maps_service.get_suggested_areas(
            request.location, request.business_type
        )

        recommendation = self._generate_recommendation(market_score, competitor_count)

        return AnalysisResult(
            location=request.location,
            business_type=request.business_type,
            trending_keywords=trending_keywords,
            competitor_count=competitor_count,
            sentiment_score=sentiment_score,
            recommendation=recommendation,
            market_score=market_score,
            suggested_locations=suggested_locations
        )

    def _calculate_sentiment(self, business_type: str, location: str) -> float:
        base_score = 0.7
        business_factors = {
            'gym': 0.1, 'restaurant': 0.0, 'cafe': 0.15, 
            'salon': 0.08, 'retail store': -0.05
        }
        location_factors = {
            'chennai': 0.05, 'bangalore': 0.1, 'mumbai': 0.08,
            'delhi': 0.03, 'hyderabad': 0.07, 'kolkata': 0.04, 'pune': 0.09
        }
        
        business_adjust = business_factors.get(business_type.lower(), 0.0)
        location_adjust = location_factors.get(location.lower(), 0.0)
        
        final_score = base_score + business_adjust + location_adjust
        return max(0.1, min(0.95, final_score))

    def _calculate_market_score(self, competitors: int, sentiment: float) -> float:
        comp_score = max(0, 1 - (competitors / 100))
        market_score = (comp_score * 0.6 + sentiment * 0.4) * 100
        return round(market_score, 1)

    def _generate_recommendation(self, market_score: float, competitor_count: int) -> str:
        if market_score >= 70 and competitor_count < 50:
            return "🚀 EXCELLENT POTENTIAL: High market score with low competition. Strongly recommended for investment."
        elif market_score >= 60:
            return "✅ GOOD POTENTIAL: Favorable market conditions with moderate competition. Recommended for strategic expansion."
        elif market_score >= 50:
            return "⚠️ MODERATE POTENTIAL: Competitive market with average potential. Consider niche positioning."
        else:
            return "❌ CHALLENGING MARKET: High competition or unfavorable conditions. Consider alternative locations or business models."

# API Endpoints
analyzer = AnalysisService()

@app.post("/analyze", response_model=AnalysisResult)
def analyze_location(request: SearchRequest):
    try:
        result = analyzer.analyze_location(request)
        
        # Store in database
        conn = sqlite3.connect('geo_keyword.db')
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO search_queries 
            (location, business_type, keywords, competitor_count, sentiment_score, recommendation) 
            VALUES (?, ?, ?, ?, ?, ?)""",
            (request.location, request.business_type, json.dumps(result.trending_keywords), 
             result.competitor_count, result.sentiment_score, result.recommendation)
        )
        conn.commit()
        conn.close()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
def get_search_history():
    conn = sqlite3.connect('geo_keyword.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM search_queries ORDER BY created_at DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": row[0],
            "location": row[1],
            "business_type": row[2],
            "keywords": json.loads(row[3]) if row[3] else [],
            "competitor_count": row[4],
            "sentiment_score": row[5],
            "recommendation": row[6],
            "created_at": row[7]
        }
        for row in rows
    ]

@app.get("/locations")
def get_supported_locations():
    return {
        "cities": ["Chennai", "Bangalore", "Mumbai", "Delhi", "Hyderabad", "Kolkata", "Pune"],
        "business_types": ["Gym", "Restaurant", "Cafe", "Salon", "Retail Store"]
    }

@app.get("/")
def root():
    return {"message": "Geo-Keyword Finder API is running! No API keys required."}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Geo-Keyword Finder Backend...")
    print("📊 No API Keys Required - Using Mock Data")
    print("🌐 Server will run on: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)