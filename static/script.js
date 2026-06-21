/* ============================================================
   QUY NHƠN SMART TRAVEL — JavaScript Engine
   Features: Tab nav, Language i18n, Hero slideshow, Particles,
   Weather fetch, Places/Hotels/Food dynamic loading,
   AI Chat, Itinerary planner + Re-plan display,
   Google Maps integration, Place modal
   ============================================================ */

'use strict';

// ============================================================
// STATE
// ============================================================
const App = {
  currentTab: 'home',
  currentLang: 'vi',
  currentSlide: 0,
  slideTimer: null,
  rawItineraryData: null,
  allPlaces: [],
  allHotels: [],
  allRestaurants: [],
  selectedPlace: null,
  chatHistory: [],
  isChatLoading: false
};

// ============================================================
// i18n TRANSLATIONS
// ============================================================
const i18n = {
  vi: {
    nav_home: 'Trang chủ', nav_itinerary: 'Lộ trình', nav_hotels: 'Khách sạn',
    nav_food: 'Ẩm thực', nav_chat: 'AI Chat',
    hero_badge: 'AI-Powered Travel Planning · Quy Nhơn 2025',
    hero_title1: 'Quy Nhơn', hero_title2: 'Biển Xanh · Hồn Việt',
    hero_subtitle: 'Khám phá Kỳ Co, Eo Gió & những hương vị không thể quên — được AI lên kế hoạch cho bạn',
    hero_cta_plan: 'Lên lịch trình ngay', hero_cta_chat: 'Hỏi AI về Quy Nhơn',
    stat_places: 'Địa điểm hot', stat_agents: 'AI Agents', stat_langs: 'Ngôn ngữ',
    scroll_down: 'Cuộn xuống',
    eyebrow_trending: 'Hot mùa này', places_title: 'Địa Điểm Nổi Tiếng',
    places_desc: 'Những điểm đến được yêu thích nhất tại Quy Nhơn mùa này',
    filter_all: 'Tất cả', filter_beach: 'Biển', filter_island: 'Đảo',
    filter_scenic: 'Check-in', filter_culture: 'Văn hóa',
    filter_budget: 'Bình dân', filter_midrange: 'Trung cấp', filter_luxury: 'Cao cấp',
    filter_breakfast: 'Ăn sáng', filter_lunch: 'Ăn trưa', filter_dinner: 'Ăn tối',
    loading_places: 'Đang tải địa điểm...', loading_hotels: 'Đang tải khách sạn...', loading_food: 'Đang tải quán ăn...',
    feat1_title: '6 AI Agents', feat1_desc: 'Lịch trình, Thời tiết, Ẩm thực, Đặt phòng, Hướng dẫn, Dịch thuật — hoạt động song song',
    feat2_title: 'Google Maps Tích hợp', feat2_desc: 'Xem bản đồ và chỉ đường ngay trong web, không cần chuyển tab',
    feat3_title: 'Re-plan Thông Minh', feat3_desc: 'Khi trời mưa hoặc vượt budget, AI tự động tạo lịch trình thay thế',
    feat4_title: '4 Ngôn ngữ', feat4_desc: 'Hỗ trợ Việt, Anh, Nhật, Hàn — dành cho cả khách quốc tế',
    itin_page_title: 'Lên Lịch Trình AI', itin_page_sub: 'Điền thông tin — AI sẽ thiết kế chuyến đi hoàn hảo cho bạn',
    form_title: 'Tùy chỉnh chuyến đi', form_dest: 'Điểm đến', form_days: 'Số ngày',
    form_budget: 'Ngân sách/ngày', form_lang: 'Ngôn ngữ kết quả',
    form_weather: 'Mô phỏng thời tiết', form_kids: 'Có trẻ nhỏ đi cùng',
    form_prefs: 'Sở thích (tuỳ chọn)', form_submit: 'Tạo Lịch Trình AI',
    presets_label: 'Gợi ý nhanh:',
    placeholder_title: 'Sẵn sàng khám phá Quy Nhơn?',
    placeholder_desc: 'Điền thông tin bên trái và nhấn "Tạo Lịch Trình AI" để bắt đầu',
    progress_title: 'AI đang phân tích & thiết kế lịch trình...',
    map_title: 'Bản đồ lịch trình', timeline_title: 'Lịch trình chi tiết',
    food_suggestions_title: 'Gợi ý ẩm thực theo lịch trình',
    weather_alerts_title: 'Cảnh báo thời tiết',
    btn_back: 'Tìm lại', btn_download: 'Tải lịch trình',
    hotels_page_title: 'Nơi Lưu Trú Quy Nhơn',
    hotels_page_sub: 'Từ hostel backpacker đến resort 5 sao — phù hợp mọi ngân sách',
    food_page_title: 'Ẩm Thực Quy Nhơn',
    food_page_sub: 'Những hương vị đặc trưng không thể bỏ qua — bình dân & ngon',
    chat_page_title: 'AI Travel Assistant', chat_page_sub: 'Hỏi bất cứ điều gì về du lịch Quy Nhơn',
    chat_suggest_title: '💡 Câu hỏi gợi ý',
    chat_welcome: 'Xin chào! 👋 Tôi là AI trợ lý du lịch Quy Nhơn.<br>Hỏi tôi bất cứ điều gì về biển đẹp, đặc sản ngon, khách sạn phù hợp — tôi sẵn sàng giúp bạn! 🌊',
    chat_online: 'Đang hoạt động', chat_placeholder: 'Hỏi về Quy Nhơn...',
    suggest1: 'Thời điểm tốt nhất để đến Quy Nhơn?',
    suggest2: 'Cách di chuyển đến Quy Nhơn?',
    suggest3: 'Đặc sản không thể bỏ qua?',
    suggest4: 'Kỳ Co vs Eo Gió — khác nhau thế nào?',
    suggest5: 'Ngân sách 3 ngày cần bao nhiêu?',
    suggest6: 'Lưu ý khi tắm biển Quy Nhơn?',
    footer_desc: 'Powered by Gemini AI · OpenWeatherMap · Google Maps',
    modal_maps: 'Xem trên Maps', modal_add_itin: 'Thêm vào lịch trình',
    modal_nearby_title: '📍 Vị trí & Tiện ích gần đây'
  },
  en: {
    nav_home: 'Home', nav_itinerary: 'Itinerary', nav_hotels: 'Hotels',
    nav_food: 'Food', nav_chat: 'AI Chat',
    hero_badge: 'AI-Powered Travel Planning · Quy Nhon 2025',
    hero_title1: 'Quy Nhon', hero_title2: 'Blue Sea · Vietnamese Soul',
    hero_subtitle: 'Discover Ky Co, Eo Gio & unforgettable flavors — AI-planned just for you',
    hero_cta_plan: 'Plan my trip now', hero_cta_chat: 'Ask AI about Quy Nhon',
    stat_places: 'Hot destinations', stat_agents: 'AI Agents', stat_langs: 'Languages',
    scroll_down: 'Scroll down',
    eyebrow_trending: 'Trending this season', places_title: 'Famous Destinations',
    places_desc: 'The most loved spots in Quy Nhon this season',
    filter_all: 'All', filter_beach: 'Beach', filter_island: 'Island',
    filter_scenic: 'Scenic', filter_culture: 'Culture',
    filter_budget: 'Budget', filter_midrange: 'Mid-range', filter_luxury: 'Luxury',
    filter_breakfast: 'Breakfast', filter_lunch: 'Lunch', filter_dinner: 'Dinner',
    loading_places: 'Loading destinations...', loading_hotels: 'Loading hotels...', loading_food: 'Loading restaurants...',
    feat1_title: '6 AI Agents', feat1_desc: 'Itinerary, Weather, Food, Booking, Guide, Translation — running in parallel',
    feat2_title: 'Google Maps Integrated', feat2_desc: 'View maps and directions right in the app, no tab switching',
    feat3_title: 'Smart Re-plan', feat3_desc: 'When it rains or exceeds budget, AI automatically creates an alternative itinerary',
    feat4_title: '4 Languages', feat4_desc: 'Vietnamese, English, Japanese, Korean — for international travelers',
    itin_page_title: 'AI Itinerary Planner', itin_page_sub: 'Fill in your details — AI designs the perfect trip for you',
    form_title: 'Customize your trip', form_dest: 'Destination', form_days: 'Number of days',
    form_budget: 'Budget/day', form_lang: 'Result language',
    form_weather: 'Weather simulation', form_kids: 'Traveling with kids',
    form_prefs: 'Preferences (optional)', form_submit: 'Create AI Itinerary',
    presets_label: 'Quick suggestions:',
    placeholder_title: 'Ready to explore Quy Nhon?',
    placeholder_desc: 'Fill in the details and click "Create AI Itinerary" to get started',
    progress_title: 'AI is analyzing & designing your itinerary...',
    map_title: 'Itinerary Map', timeline_title: 'Detailed Itinerary',
    food_suggestions_title: 'Food recommendations along your route',
    weather_alerts_title: 'Weather Alerts',
    btn_back: 'Search again', btn_download: 'Download itinerary',
    hotels_page_title: 'Stay in Quy Nhon',
    hotels_page_sub: 'From backpacker hostels to 5-star resorts — for every budget',
    food_page_title: 'Quy Nhon Cuisine',
    food_page_sub: 'Unforgettable local specialties — affordable & delicious',
    chat_page_title: 'AI Travel Assistant', chat_page_sub: 'Ask anything about Quy Nhon travel',
    chat_suggest_title: '💡 Suggested Questions',
    chat_welcome: 'Hello! 👋 I\'m your Quy Nhon AI travel assistant.<br>Ask me anything about beautiful beaches, local specialties, or accommodations — I\'m here to help! 🌊',
    chat_online: 'Online', chat_placeholder: 'Ask about Quy Nhon...',
    suggest1: 'Best time to visit Quy Nhon?',
    suggest2: 'How to travel to Quy Nhon?',
    suggest3: 'Must-try local specialties?',
    suggest4: 'Ky Co vs Eo Gio — what\'s different?',
    suggest5: 'Budget needed for 3 days?',
    suggest6: 'Tips for swimming at Quy Nhon beaches?',
    footer_desc: 'Powered by Gemini AI · OpenWeatherMap · Google Maps',
    modal_maps: 'View on Maps', modal_add_itin: 'Add to itinerary',
    modal_nearby_title: '📍 Location & Nearby Amenities'
  },
  ja: {
    nav_home: 'ホーム', nav_itinerary: '旅程', nav_hotels: 'ホテル',
    nav_food: 'グルメ', nav_chat: 'AIチャット',
    hero_badge: 'AI旅行プランニング · クイニョン 2025',
    hero_title1: 'クイニョン', hero_title2: '青い海 · ベトナムの魂',
    hero_subtitle: 'キーコー、エーオジョー & 忘れられない味を発見 — AIが完璧に計画',
    hero_cta_plan: '旅程を今すぐ計画', hero_cta_chat: 'クイニョンについてAIに質問',
    stat_places: 'ホットスポット', stat_agents: 'AIエージェント', stat_langs: '言語',
    scroll_down: 'スクロール',
    eyebrow_trending: 'この季節のトレンド', places_title: '人気観光スポット',
    places_desc: 'クイニョンで今季最も人気のスポット',
    filter_all: 'すべて', filter_beach: 'ビーチ', filter_island: '島',
    filter_scenic: '景観', filter_culture: '文化',
    filter_budget: '格安', filter_midrange: 'ミドル', filter_luxury: '豪華',
    filter_breakfast: '朝食', filter_lunch: 'ランチ', filter_dinner: '夕食',
    loading_places: 'スポットを読み込み中...', loading_hotels: 'ホテルを読み込み中...', loading_food: 'レストランを読み込み中...',
    feat1_title: '6つのAIエージェント', feat1_desc: '旅程、天気、グルメ、予約、ガイド、翻訳 — 並列処理',
    feat2_title: 'Googleマップ統合', feat2_desc: 'アプリ内でマップと道案内を確認、タブ切替不要',
    feat3_title: 'スマート再計画', feat3_desc: '雨天や予算超過時にAIが自動で代替旅程を作成',
    feat4_title: '4言語対応', feat4_desc: 'ベトナム語、英語、日本語、韓国語 — 外国人旅行者にも対応',
    itin_page_title: 'AI旅程プランナー', itin_page_sub: '情報を入力 — AIが完璧な旅行を設計します',
    form_title: '旅行のカスタマイズ', form_dest: '目的地', form_days: '日数',
    form_budget: '1日の予算', form_lang: '結果言語',
    form_weather: '天気シミュレーション', form_kids: '子供連れ',
    form_prefs: '好み（オプション）', form_submit: 'AI旅程を作成',
    presets_label: 'クイック提案:',
    placeholder_title: 'クイニョンを探索する準備はできましたか？',
    placeholder_desc: '詳細を入力して「AI旅程を作成」をクリックして始めましょう',
    progress_title: 'AIが旅程を分析・設計中...',
    map_title: '旅程マップ', timeline_title: '詳細旅程',
    food_suggestions_title: 'ルート沿いのグルメ提案',
    weather_alerts_title: '天気警報',
    btn_back: '再検索', btn_download: '旅程をダウンロード',
    hotels_page_title: 'クイニョンの宿泊施設',
    hotels_page_sub: 'バックパッカーホステルから5つ星リゾートまで',
    food_page_title: 'クイニョングルメ',
    food_page_sub: '絶対に外せないローカルグルメ — お手頃＆美味',
    chat_page_title: 'AI旅行アシスタント', chat_page_sub: 'クイニョン旅行について何でも聞いてください',
    chat_suggest_title: '💡 おすすめ質問',
    chat_welcome: 'こんにちは！👋 クイニョンのAI旅行アシスタントです。<br>美しいビーチ、ローカルグルメ、宿泊施設について何でもお聞きください！🌊',
    chat_online: 'オンライン', chat_placeholder: 'クイニョンについて質問...',
    suggest1: 'クイニョン訪問のベストシーズンは？',
    suggest2: 'クイニョンへのアクセス方法は？',
    suggest3: '必食のローカルグルメは？',
    suggest4: 'キーコーとエーオジョーの違いは？',
    suggest5: '3日間の予算はいくら必要？',
    suggest6: 'ビーチで泳ぐ際の注意事項は？',
    footer_desc: 'Gemini AI · OpenWeatherMap · Google Maps 搭載',
    modal_maps: 'マップで見る', modal_add_itin: '旅程に追加',
    modal_nearby_title: '📍 場所と周辺施設'
  },
  ko: {
    nav_home: '홈', nav_itinerary: '일정', nav_hotels: '호텔',
    nav_food: '음식', nav_chat: 'AI 채팅',
    hero_badge: 'AI 여행 계획 · 꾸이년 2025',
    hero_title1: '꾸이년', hero_title2: '푸른 바다 · 베트남의 영혼',
    hero_subtitle: '키꼬, 에오지오 & 잊을 수 없는 맛 발견 — AI가 완벽하게 계획',
    hero_cta_plan: '지금 일정 계획하기', hero_cta_chat: '꾸이년에 대해 AI에게 물어보기',
    stat_places: '핫 명소', stat_agents: 'AI 에이전트', stat_langs: '언어',
    scroll_down: '스크롤',
    eyebrow_trending: '이 시즌 트렌드', places_title: '인기 명소',
    places_desc: '이 시즌 꾸이년에서 가장 사랑받는 명소',
    filter_all: '전체', filter_beach: '해변', filter_island: '섬',
    filter_scenic: '경관', filter_culture: '문화',
    filter_budget: '저렴', filter_midrange: '중간', filter_luxury: '고급',
    filter_breakfast: '아침', filter_lunch: '점심', filter_dinner: '저녁',
    loading_places: '명소 로딩 중...', loading_hotels: '호텔 로딩 중...', loading_food: '음식점 로딩 중...',
    feat1_title: '6개 AI 에이전트', feat1_desc: '일정, 날씨, 음식, 예약, 가이드, 번역 — 병렬 실행',
    feat2_title: '구글 맵 통합', feat2_desc: '앱 내에서 지도와 길 찾기 확인, 탭 전환 불필요',
    feat3_title: '스마트 재계획', feat3_desc: '비나 예산 초과 시 AI가 자동으로 대체 일정 생성',
    feat4_title: '4개 언어 지원', feat4_desc: '베트남어, 영어, 일본어, 한국어 — 외국인 여행자 지원',
    itin_page_title: 'AI 일정 플래너', itin_page_sub: '정보를 입력하세요 — AI가 완벽한 여행을 설계합니다',
    form_title: '여행 맞춤 설정', form_dest: '목적지', form_days: '일수',
    form_budget: '하루 예산', form_lang: '결과 언어',
    form_weather: '날씨 시뮬레이션', form_kids: '어린이 동반',
    form_prefs: '선호도 (선택)', form_submit: 'AI 일정 생성',
    presets_label: '빠른 제안:',
    placeholder_title: '꾸이년 탐험 준비가 됐나요?',
    placeholder_desc: '정보를 입력하고 "AI 일정 생성"을 클릭하여 시작하세요',
    progress_title: 'AI가 일정을 분석 및 설계 중...',
    map_title: '일정 지도', timeline_title: '상세 일정',
    food_suggestions_title: '경로 따라 음식 추천',
    weather_alerts_title: '날씨 경보',
    btn_back: '다시 검색', btn_download: '일정 다운로드',
    hotels_page_title: '꾸이년 숙박',
    hotels_page_sub: '백패커 호스텔부터 5성급 리조트까지',
    food_page_title: '꾸이년 미식',
    food_page_sub: '놓칠 수 없는 현지 특산품 — 저렴하고 맛있는',
    chat_page_title: 'AI 여행 어시스턴트', chat_page_sub: '꾸이년 여행에 대해 무엇이든 물어보세요',
    chat_suggest_title: '💡 추천 질문',
    chat_welcome: '안녕하세요! 👋 꾸이년 AI 여행 어시스턴트입니다.<br>아름다운 해변, 현지 특산품, 숙박 시설에 대해 무엇이든 물어보세요! 🌊',
    chat_online: '온라인', chat_placeholder: '꾸이년에 대해 질문...',
    suggest1: '꾸이년 방문 최적 시기는?',
    suggest2: '꾸이년 교통편은?',
    suggest3: '꼭 먹어야 할 현지 특산품은?',
    suggest4: '키꼬 vs 에오지오 차이점은?',
    suggest5: '3일 여행 예산은?',
    suggest6: '꾸이년 해변 수영 주의사항은?',
    footer_desc: 'Gemini AI · OpenWeatherMap · Google Maps 탑재',
    modal_maps: '지도에서 보기', modal_add_itin: '일정에 추가',
    modal_nearby_title: '📍 위치 및 주변 시설'
  }
};

// ============================================================
// LANGUAGE SYSTEM
// ============================================================
function switchLanguage(lang) {
  App.currentLang = lang;
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.lang === lang);
  });
  applyTranslations();
  updateChatLangBadge();
  updateChatInputPlaceholder();
  updateSuggestButtons();
}

function applyTranslations() {
  const t = i18n[App.currentLang] || i18n.vi;
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.dataset.i18n;
    if (t[key]) {
      if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
        el.placeholder = t[key];
      } else {
        el.innerHTML = t[key];
      }
    }
  });
}

function t(key) {
  return (i18n[App.currentLang] || i18n.vi)[key] || key;
}

function updateChatLangBadge() {
  const badges = { vi:'🇻🇳 VI', en:'🇺🇸 EN', ja:'🇯🇵 JP', ko:'🇰🇷 KR' };
  document.getElementById('chatLangBadge').textContent = badges[App.currentLang] || '🇻🇳 VI';
}

function updateChatInputPlaceholder() {
  const placeholders = { vi:'Hỏi về Quy Nhơn...', en:'Ask about Quy Nhon...', ja:'クイニョンについて質問...', ko:'꾸이년에 대해 질문...' };
  document.getElementById('chatInput').placeholder = placeholders[App.currentLang] || 'Ask...';
}

function updateSuggestButtons() {
  document.querySelectorAll('.suggest-btn').forEach(btn => {
    const text = btn.dataset[`text${App.currentLang.charAt(0).toUpperCase() + App.currentLang.slice(1)}`];
    const span = btn.querySelector('span');
    if (text && span) span.textContent = text.replace(/^[^\s]+ /, '');
  });
}

// ============================================================
// TAB NAVIGATION
// ============================================================
function switchTab(tab) {
  App.currentTab = tab;
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
  const page = document.getElementById(`page-${tab}`);
  const navTab = document.getElementById(`tab-${tab}`);
  if (page) page.classList.add('active');
  if (navTab) navTab.classList.add('active');
  window.scrollTo({ top: 0, behavior: 'smooth' });

  // Lazy load tab data
  if (tab === 'hotels' && App.allHotels.length === 0) loadHotels();
  if (tab === 'food' && App.allRestaurants.length === 0) loadRestaurants();
}

// ============================================================
// HERO SLIDESHOW
// ============================================================
function initHeroSlideshow() {
  const slides = document.querySelectorAll('.hero-slide');
  const dots = document.querySelectorAll('.dot');
  if (!slides.length) return;

  function goTo(n) {
    slides[App.currentSlide].classList.remove('active');
    dots[App.currentSlide].classList.remove('active');
    App.currentSlide = (n + slides.length) % slides.length;
    slides[App.currentSlide].classList.add('active');
    dots[App.currentSlide].classList.add('active');
  }

  window.goToSlide = goTo;
  App.slideTimer = setInterval(() => goTo(App.currentSlide + 1), 5000);
}

// ============================================================
// PARTICLES
// ============================================================
function initParticles() {
  const container = document.getElementById('heroParticles');
  if (!container) return;
  for (let i = 0; i < 25; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    p.style.cssText = `
      left: ${Math.random() * 100}%;
      width: ${Math.random() * 4 + 2}px;
      height: ${Math.random() * 4 + 2}px;
      animation-duration: ${Math.random() * 15 + 10}s;
      animation-delay: ${Math.random() * 10}s;
      opacity: ${Math.random() * 0.6 + 0.2};
    `;
    container.appendChild(p);
  }
}

// ============================================================
// NAVBAR SCROLL
// ============================================================
function initNavbarScroll() {
  window.addEventListener('scroll', () => {
    document.getElementById('mainNav').classList.toggle('scrolled', window.scrollY > 60);
  }, { passive: true });
}

// ============================================================
// WEATHER
// ============================================================
async function fetchWeather() {
  try {
    const resp = await fetch('/api/weather/quynhon');
    const data = await resp.json();
    if (data.success) {
      document.getElementById('weatherTemp').textContent = `${data.temp}°C`;
      document.getElementById('weatherCond').textContent = data.condition;
      document.getElementById('heroTemp').textContent = `${data.temp}°`;
      if (data.icon) {
        const img = document.getElementById('weatherIcon');
        img.src = data.icon;
        img.style.display = 'block';
      }
    }
  } catch (e) {
    console.warn('Weather fetch failed:', e);
  }
}

async function fetchForecast() {
  try {
    const resp = await fetch('/api/forecast/quynhon');
    const data = await resp.json();
    if (data.success && data.forecast) {
      renderForecast(data.forecast);
    }
  } catch (e) {
    console.warn('Forecast fetch failed:', e);
    document.getElementById('forecastContent').innerHTML = '<span class="forecast-loading">Không thể tải dự báo thời tiết</span>';
  }
}

function renderForecast(forecast) {
  const dayNames = { vi:['CN','T2','T3','T4','T5','T6','T7'], en:['Sun','Mon','Tue','Wed','Thu','Fri','Sat'], ja:['日','月','火','水','木','金','土'], ko:['일','월','화','수','목','금','토'] };
  const html = forecast.map(f => {
    const d = new Date(f.date);
    const dayName = (dayNames[App.currentLang] || dayNames.vi)[d.getDay()];
    const isRainy = f.rain_prob >= 0.6;
    return `
      <div class="forecast-day${isRainy ? ' rainy' : ''}">
        <span class="fc-date">${dayName} ${d.getDate()}/${d.getMonth()+1}</span>
        <img src="${f.icon}" alt="${f.condition}">
        <span class="fc-temp">${f.temp_max}° / ${f.temp_min}°</span>
        <span class="fc-cond">${f.condition}</span>
        ${isRainy ? `<span class="rain-chance">🌧️ ${Math.round(f.rain_prob*100)}%</span>` : ''}
      </div>
    `;
  }).join('');
  document.getElementById('forecastContent').innerHTML = html;
}

// ============================================================
// PLACES
// ============================================================
async function loadPlaces() {
  try {
    const resp = await fetch('/api/places');
    const data = await resp.json();
    if (data.success) {
      App.allPlaces = data.places;
      renderPlaces(App.allPlaces);
    }
  } catch (e) {
    document.getElementById('placesGrid').innerHTML = '<div class="loading-placeholder"><p>Không thể tải dữ liệu địa điểm</p></div>';
  }
}

function renderPlaces(places) {
  const grid = document.getElementById('placesGrid');
  if (!places.length) { grid.innerHTML = '<div class="loading-placeholder"><p>Không có địa điểm nào</p></div>'; return; }

  grid.innerHTML = places.map((p, idx) => {
    const isFree = p.price === 0;
    const isHot = p.rating >= 4.8;
    const badges = [
      isHot ? `<span class="pbadge pbadge-hot">🔥 Hot</span>` : '',
      isFree ? `<span class="pbadge pbadge-free">✓ Free</span>` : '',
      p.tags.includes('GenZ Hot') ? `<span class="pbadge pbadge-trending">⚡ Trending</span>` : ''
    ].filter(Boolean).join('');

    const tags = p.tags.slice(0, 3).map(tag => `<span class="ptag">${tag}</span>`).join('');

    return `
      <div class="place-card" onclick="openPlaceModal(${idx})" data-type="${p.type}">
        <div class="place-card-img-wrap">
          <img src="${p.image_url}" alt="${p.name}" class="place-card-img" loading="lazy">
          <div class="place-card-overlay"></div>
          <div class="place-card-badges">${badges}</div>
          <div class="place-card-rating">⭐ ${p.rating}</div>
        </div>
        <div class="place-card-body">
          <div class="place-card-tags">${tags}</div>
          <h3 class="place-card-title">${p.name}</h3>
          <p class="place-card-desc">${p.description}</p>
          <div class="place-card-footer">
            <div class="place-card-price">
              ${isFree ? '<strong>Miễn phí</strong>' : `<strong>${p.price.toLocaleString('vi-VN')}₫</strong>`}
              · ⏱️ ${p.avg_duration}
            </div>
            <div class="place-card-cta">Khám phá <i class="fa-solid fa-arrow-right"></i></div>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

function filterPlaces(type) {
  document.querySelectorAll('#placesFilter .filter-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.filter === type);
  });
  const filtered = type === 'all' ? App.allPlaces : App.allPlaces.filter(p => p.type === type);
  renderPlaces(filtered);
}

// ============================================================
// PLACE MODAL
// ============================================================
let currentModalPlace = null;

function openPlaceModal(pOrIdx, type = 'place') {
  let p = null;
  if (type === 'hotel') p = App.allHotels[pOrIdx];
  else if (type === 'food') p = App.allRestaurants[pOrIdx];
  else p = App.allPlaces[pOrIdx];

  if (!p) return;
  currentModalPlace = p;

  document.getElementById('modalImg').src = p.image_url || '';
  document.getElementById('modalImg').alt = p.name || '';
  document.getElementById('modalName').textContent = p.name || '';
  document.getElementById('modalRating').innerHTML = `⭐ ${p.rating || 5} / 5`;
  
  const price = p.price !== undefined ? p.price : (p.price_per_night !== undefined ? p.price_per_night : (p.avg_price_person !== undefined ? p.avg_price_person : 0));
  const priceLabel = p.price_per_night ? '/đêm' : '';
  document.getElementById('modalPrice').textContent = price === 0 ? '✓ Miễn phí' : `Giá: ${price.toLocaleString('vi-VN')}₫${priceLabel}`;
  
  const duration = p.avg_duration || p.type || p.specialty || '';
  document.getElementById('modalDuration').textContent = `📌 ${duration}`;
  document.getElementById('modalDesc').textContent = p.description || '';
  document.getElementById('modalTips').textContent = p.tips || p.must_try || '';
  document.getElementById('modalTipsWrap').style.display = (p.tips || p.must_try) ? 'flex' : 'none';

  const tags = p.tags || [];
  const badges = [
    p.rating >= 4.8 ? `<span class="pbadge pbadge-hot">🔥 Top Pick</span>` : '',
    tags.includes('GenZ Hot') ? `<span class="pbadge pbadge-trending">⚡ GenZ</span>` : ''
  ].filter(Boolean).join('');
  document.getElementById('modalBadges').innerHTML = badges;

  const reviewsHtml = (p.reviews || []).map(r => `
    <div class="modal-review-item">
      <strong>${r.user}</strong><br>${r.text}
    </div>
  `).join('');
  document.getElementById('modalReviews').innerHTML = reviewsHtml || '<div class="modal-review-item">Chưa có đánh giá</div>';

  let mapSrc = '';
  if (p.coordinate && p.coordinate.lat) {
    mapSrc = `https://maps.google.com/?q=${p.coordinate.lat},${p.coordinate.lon}&z=15&output=embed`;
  } else if (p.google_maps_url) {
    mapSrc = p.google_maps_url + '&z=15&output=embed';
  } else {
    const q = encodeURIComponent(p.name + ' ' + (p.address || 'Quy Nhơn'));
    mapSrc = `https://maps.google.com/?q=${q}&z=15&output=embed`;
  }
  document.getElementById('modalMapIframe').src = mapSrc;

  const modal = document.getElementById('placeModal');
  modal.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closePlaceModal(e) {
  if (e && e.target !== document.getElementById('placeModal') && !e.target.closest('.modal-close')) return;
  document.getElementById('placeModal').classList.remove('open');
  document.body.style.overflow = '';
}

function openPlaceOnMap() {
  if (!currentModalPlace) return;
  let url = currentModalPlace.google_maps_url;
  if (!url && currentModalPlace.coordinate && currentModalPlace.coordinate.lat) {
    url = `https://maps.google.com/?q=${currentModalPlace.coordinate.lat},${currentModalPlace.coordinate.lon}`;
  }
  if (!url) {
    url = `https://maps.google.com/?q=${encodeURIComponent(currentModalPlace.name)}`;
  }
  window.open(url, '_blank');
}

function addToItinerary() {
  if (!currentModalPlace) return;
  const dest = document.getElementById('destination');
  if (dest) dest.value = 'Quy Nhơn';
  closePlaceModal();
  switchTab('itinerary');
  document.getElementById('preferences').value = `Muốn đến ${currentModalPlace.name}`;
}

// ============================================================
// HOTELS
// ============================================================
async function loadHotels() {
  try {
    const resp = await fetch('/api/hotels');
    const data = await resp.json();
    if (data.success) {
      App.allHotels = data.hotels;
      renderHotels(App.allHotels);
    }
  } catch (e) {
    document.getElementById('hotelsGrid').innerHTML = '<div class="loading-placeholder"><p>Không thể tải dữ liệu khách sạn</p></div>';
  }
}

function renderHotels(hotels) {
  const grid = document.getElementById('hotelsGrid');
  if (!hotels.length) { grid.innerHTML = '<div class="loading-placeholder"><p>Không có khách sạn nào</p></div>'; return; }

  grid.innerHTML = hotels.map((h, idx) => {
    const budgetClass = { 'Bình dân': 'budget', 'Trung cấp': 'midrange', 'Cao cấp': 'luxury' }[h.budget_level] || 'budget';
    const stars = '⭐'.repeat(Math.round(h.rating));
    const amenitiesHtml = (h.amenities || []).slice(0, 4).map(a => `<span class="amenity-tag">${a}</span>`).join('');

    return `
      <div class="hotel-card" onclick="selectHotel(${idx})">
        <div class="hotel-card-img">
          <img src="${h.image_url}" alt="${h.name}" loading="lazy">
          <div class="hotel-badge ${budgetClass}">${h.budget_level}</div>
        </div>
        <div class="hotel-card-body">
          <h3 class="hotel-name">${h.name}</h3>
          <p class="hotel-type">${h.type}</p>
          <div class="hotel-meta">
            <span class="hotel-rating">${stars} ${h.rating}</span>
            <span class="hotel-address"><i class="fa-solid fa-location-dot"></i> ${h.address}</span>
          </div>
          <div class="hotel-amenities">${amenitiesHtml}</div>
          <p style="font-size:0.82rem;color:#64748b;line-height:1.5;margin-bottom:0.75rem">${h.description}</p>
          <div class="hotel-footer">
            <div class="hotel-price">
              <strong>${h.price_per_night.toLocaleString('vi-VN')}₫</strong>
              <span>/đêm</span>
            </div>
            <button class="hotel-map-btn" onclick="event.stopPropagation();showHotelMap(${idx})">
              <i class="fa-solid fa-map-location-dot"></i> Xem Maps
            </button>
          </div>
          ${(h.reviews || []).length ? `<div class="food-reviews">${h.reviews.slice(0,1).map(r => `<div class="review-item">${r.user}: "${r.text}"</div>`).join('')}</div>` : ''}
        </div>
      </div>
    `;
  }).join('');
}

function filterHotels(level) {
  document.querySelectorAll('#page-hotels .filter-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.filter === level);
  });
  const filtered = level === 'all' ? App.allHotels : App.allHotels.filter(h => h.budget_level === level);
  renderHotels(filtered);
}

function showHotelMap(idx) {
  const h = App.allHotels[idx];
  if (!h) return;
  const section = document.getElementById('hotelMapSection');
  section.classList.remove('hidden');
  document.getElementById('hotelMapTitle').textContent = `📍 ${h.name}`;
  const q = encodeURIComponent(h.name + ' ' + h.address);
  document.getElementById('hotelMapIframe').src = `https://maps.google.com/?q=${q}&output=embed`;
  
  // Show nearby amenity chips
  const nearby = document.getElementById('nearbyAmenities');
  nearby.innerHTML = `
    <div class="nearby-chip" onclick="openNearby('nhà hàng gần ${encodeURIComponent(h.address)}')"><i class="fa-solid fa-utensils"></i> Nhà hàng gần đây</div>
    <div class="nearby-chip" onclick="openNearby('ATM gần ${encodeURIComponent(h.address)}')"><i class="fa-solid fa-building-columns"></i> ATM</div>
    <div class="nearby-chip" onclick="openNearby('siêu thị gần ${encodeURIComponent(h.address)}')"><i class="fa-solid fa-store"></i> Siêu thị</div>
    <div class="nearby-chip" onclick="openNearby('cafe gần ${encodeURIComponent(h.address)}')"><i class="fa-solid fa-mug-hot"></i> Cà phê</div>
  `;
  section.scrollIntoView({ behavior: 'smooth' });
}

function openNearby(query) {
  window.open(`https://maps.google.com/?q=${query}`, '_blank');
}

function selectHotel(idx) {
  openPlaceModal(idx, 'hotel');
}

// ============================================================
// RESTAURANTS
// ============================================================
async function loadRestaurants() {
  try {
    const resp = await fetch('/api/restaurants');
    const data = await resp.json();
    if (data.success) {
      App.allRestaurants = data.restaurants;
      renderRestaurants(App.allRestaurants);
    }
  } catch (e) {
    document.getElementById('foodGrid').innerHTML = '<div class="loading-placeholder"><p>Không thể tải dữ liệu quán ăn</p></div>';
  }
}

function renderRestaurants(restaurants) {
  const grid = document.getElementById('foodGrid');
  if (!restaurants.length) { grid.innerHTML = '<div class="loading-placeholder"><p>Không có quán ăn nào</p></div>'; return; }

  grid.innerHTML = restaurants.map((r, idx) => {
    const priceClass = { 'Bình dân': 'binh-dan', 'Trung cấp': 'trung-cap', 'Cao cấp': 'cao-cap' }[r.price_level] || 'binh-dan';
    const mealBadges = r.meal_type.map(m => `<span class="ptag">${m}</span>`).join('');
    const stars = '⭐'.repeat(Math.round(r.rating));

    return `
      <div class="food-card" onclick="openPlaceModal(${idx}, 'food')">
        <div class="food-card-img">
          <img src="${r.image_url}" alt="${r.name}" loading="lazy">
        </div>
        <div class="food-card-body">
          <div class="place-card-tags">${mealBadges}</div>
          <h3 class="food-card-name">${r.name}</h3>
          <p class="food-card-specialty">⭐ ${r.specialty}</p>
          <p class="food-card-desc">${r.description}</p>
          <p class="food-address"><i class="fa-solid fa-location-dot"></i> ${r.address}</p>
          <p class="food-hours"><i class="fa-regular fa-clock"></i> ${r.open_hours}</p>
          <div class="food-card-footer">
            <div>
              <span class="food-price-badge ${priceClass}">${r.price_level} · ${r.avg_price_person.toLocaleString('vi-VN')}₫</span>
              <div class="food-rating" style="margin-top:0.3rem">${stars} ${r.rating}</div>
            </div>
            <button class="food-map-btn" onclick="event.stopPropagation();openPlaceModal(${idx}, 'food')">
              <i class="fa-solid fa-map-location-dot"></i> Maps
            </button>
          </div>
          ${(r.reviews || []).length ? `<div class="food-reviews">${r.reviews.slice(0,1).map(rv => `<div class="review-item">${rv.user}: "${rv.text}"</div>`).join('')}</div>` : ''}
        </div>
      </div>
    `;
  }).join('');
}

function filterFood(filter) {
  document.querySelectorAll('#page-food .filter-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.filter === filter);
  });
  let filtered;
  if (filter === 'all') {
    filtered = App.allRestaurants;
  } else if (['Sáng','Trưa','Tối'].includes(filter)) {
    filtered = App.allRestaurants.filter(r => r.meal_type.includes(filter));
  } else {
    filtered = App.allRestaurants.filter(r => r.price_level === filter);
  }
  renderRestaurants(filtered);
}

function showFoodMap(idx) {
  const r = App.allRestaurants[idx];
  if (!r) return;
  const section = document.getElementById('foodMapSection');
  section.classList.remove('hidden');
  document.getElementById('foodMapTitle').textContent = `📍 ${r.name}`;
  const q = encodeURIComponent(r.name + ', ' + r.address);
  document.getElementById('foodMapIframe').src = `https://maps.google.com/?q=${q}&output=embed`;
  section.scrollIntoView({ behavior: 'smooth' });
}

// ============================================================
// ITINERARY PLANNER
// ============================================================
function applyPreset(dest, days, budget, weatherSim) {
  document.getElementById('destination').value = dest;
  document.getElementById('days').value = days;
  document.getElementById('budget').value = budget;
  document.getElementById('weatherSim').value = weatherSim;
  submitSearch();
}

function resetSearch() {
  document.getElementById('resultsContainer').classList.add('hidden');
  document.getElementById('resultsPlaceholder').classList.remove('hidden');
  document.getElementById('progressContainer').classList.add('hidden');
  document.getElementById('logArea').innerHTML = '';
}

async function submitSearch() {
  const destination = document.getElementById('destination').value.trim();
  const days = parseInt(document.getElementById('days').value);
  const budget = parseInt(document.getElementById('budget').value);
  const language = document.getElementById('resultLanguage').value;
  const weatherSim = document.getElementById('weatherSim').value;
  const hasKids = document.getElementById('hasKids').checked;
  const preferences = document.getElementById('preferences').value.trim();

  if (!destination) { alert('Vui lòng nhập điểm đến!'); return; }

  // UI: loading state
  document.getElementById('resultsPlaceholder').classList.add('hidden');
  document.getElementById('resultsContainer').classList.add('hidden');
  document.getElementById('progressContainer').classList.remove('hidden');
  document.getElementById('logArea').innerHTML = '';
  document.getElementById('currentAction').textContent = 'Khởi tạo...';
  document.getElementById('planBtn').disabled = true;

  // Reset agent chips
  document.querySelectorAll('.agent-chip').forEach(c => c.classList.remove('active', 'done'));

  try {
    const res = await fetch('/api/plan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ destination, days, budget_per_day: budget, language, has_kids: hasKids, preferences, weather_sim_mode: weatherSim })
    });
    const data = await res.json();
    const taskId = data.task_id;

    const evtSource = new EventSource(`/api/stream/${taskId}`);

    evtSource.onmessage = function(event) {
      const msg = JSON.parse(event.data);
      if (msg.type === 'log') {
        appendLog(msg.data);
        updateAgentChip(msg.data.agent);
        document.getElementById('currentAction').textContent = `${msg.data.agent} đang làm việc...`;
      } else if (msg.type === 'result') {
        evtSource.close();
        document.getElementById('progressContainer').classList.add('hidden');
        document.getElementById('planBtn').disabled = false;
        renderResults(msg.data);
      } else if (msg.type === 'error') {
        evtSource.close();
        document.getElementById('progressContainer').classList.add('hidden');
        document.getElementById('resultsPlaceholder').classList.remove('hidden');
        document.getElementById('planBtn').disabled = false;
        alert('Lỗi: ' + msg.data);
      }
    };

    evtSource.onerror = function() {
      evtSource.close();
      document.getElementById('planBtn').disabled = false;
    };

  } catch (e) {
    console.error(e);
    document.getElementById('progressContainer').classList.add('hidden');
    document.getElementById('resultsPlaceholder').classList.remove('hidden');
    document.getElementById('planBtn').disabled = false;
    alert('Không thể kết nối đến server! Hãy chắc chắn rằng server đang chạy (python server.py).');
  }
}

function appendLog(log) {
  const line = document.createElement('div');
  line.innerHTML =
    `<span style="color:#5eead4">[${log.timestamp}]</span> ` +
    `<span style="color:#4ade80;font-weight:700">${log.agent}:</span> ` +
    `<span style="color:#d1d5db">${log.action}</span>`;
  const area = document.getElementById('logArea');
  area.appendChild(line);
  area.scrollTop = area.scrollHeight;
}

function updateAgentChip(agentName) {
  const agentMap = {
    'Itinerary Agent': 'chip-itinerary',
    'Weather Agent': 'chip-weather',
    'Food Agent': 'chip-food',
    'Booking Agent': 'chip-booking',
    'Re-plan Agent': 'chip-replan',
    'Translate Agent': 'chip-translate'
  };
  // Mark previous active as done
  document.querySelectorAll('.agent-chip.active').forEach(c => {
    c.classList.remove('active');
    c.classList.add('done');
  });
  const chipId = agentMap[agentName];
  if (chipId) {
    const chip = document.getElementById(chipId);
    if (chip) chip.classList.add('active');
  }
}

function renderResults(state) {
  App.rawItineraryData = state;
  document.getElementById('resultsContainer').classList.remove('hidden');
  const dest = state.user_request?.destination || 'Quy Nhơn';
  const days = state.user_request?.days || 3;
  document.getElementById('resultTitle').textContent = `📍 ${dest} · ${days} Ngày`;

  // Scroll map to destination
  const mapSrc = `https://maps.google.com/?q=${encodeURIComponent(dest)}&z=12&output=embed`;
  document.getElementById('googleMapIframe').src = mapSrc;

  // ---- Re-plan alert ----
  const replan = state.replan || {};
  const replanAlert = document.getElementById('replanAlert');
  if (replan.rain_triggered || replan.budget_triggered) {
    replanAlert.classList.remove('hidden');
    const alerts = [];
    if (replan.rain_triggered) alerts.push('⛈️ Dự báo mưa lớn tại một số địa điểm');
    if (replan.budget_triggered) alerts.push('💸 Chi phí ước tính vượt quá ngân sách');
    document.getElementById('replanAlertTitle').textContent = '⚠️ AI phát hiện: ' + alerts.join(' & ');
    document.getElementById('replanAlertDesc').textContent = 'AI đã tạo phương án thay thế bên dưới. Chọn hoạt động phù hợp hơn!';

    let altHtml = '';
    if (replan.rain_triggered && replan.rain_alternatives?.length) {
      replan.rain_alternatives.slice(0, 3).forEach(alt => {
        altHtml += `
          <div class="replan-item">
            <div>
              <h4>🌧️ Ngày ${alt.original_day} (${alt.original_session}) → ${alt.replan_activity}</h4>
              <p>📍 ${alt.replan_location || alt.address || ''}</p>
              <p>${alt.replan_description}</p>
              <p><em>💡 ${alt.rain_tip || ''}</em></p>
            </div>
            <span style="color:#f97316;font-size:0.82rem">${alt.replan_cost_estimate || ''}</span>
          </div>`;
      });
    }
    if (replan.budget_triggered && replan.budget_alternatives) {
      const ba = replan.budget_alternatives;
      altHtml += `
        <div class="replan-item">
          <div>
            <h4>💰 Gợi ý tiết kiệm: ${ba.hotel_suggestion?.name || ''}</h4>
            <p>${ba.summary || ''}</p>
            <p>Tiết kiệm ước tính: ${ba.total_savings_estimate || ''}/ngày</p>
          </div>
        </div>`;
    }
    document.getElementById('replanAlternatives').innerHTML = altHtml;
  } else {
    replanAlert.classList.add('hidden');
  }

  // ---- Booking ----
  const bookingGrid = document.getElementById('bookingSection');
  bookingGrid.innerHTML = '';
  const hotel = state.booking?.hotel;
  const transport = state.booking?.transport;

  if (hotel || transport) {
    bookingGrid.classList.remove('hidden');
    if (hotel) {
      bookingGrid.innerHTML += `
        <div class="booking-card">
          ${hotel.image_url ? `<img src="${hotel.image_url}" style="width:100%;height:150px;object-fit:cover;border-radius:12px;margin-bottom:1rem;">` : ''}
          <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:1rem">
            <div style="width:42px;height:42px;border-radius:12px;background:#e0f2f1;color:#0d9488;display:flex;align-items:center;justify-content:center;font-size:1.2rem">
              <i class="fa-solid fa-hotel"></i>
            </div>
            <div>
              <p style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.6px;color:#94a3b8">Nơi lưu trú đề xuất</p>
              <p style="font-size:.95rem;font-weight:800;color:#0f172a">${hotel.name}</p>
            </div>
          </div>
          <p style="font-size:.875rem;color:#64748b;margin-bottom:.5rem">${hotel.type || ''} &nbsp;·&nbsp; ⭐ ${hotel.rating || '-'}/5 &nbsp;·&nbsp; 📍 ${hotel.address || ''}</p>
          <p style="font-size:1.1rem;font-weight:800;color:#0d9488">${(hotel.price_per_night || 0).toLocaleString('vi-VN')}₫<span style="font-size:.8rem;font-weight:400;color:#94a3b8">/đêm</span></p>
          <p style="font-size:.82rem;color:#94a3b8;margin-top:.5rem;font-style:italic">${hotel.description || ''}</p>
          ${hotel.fallback_used ? '<p style="font-size:.75rem;color:#f97316;margin-top:.5rem">⚠️ Đề xuất dự phòng (budget thấp)</p>' : ''}
        </div>`;
    }
    if (transport) {
      bookingGrid.innerHTML += `
        <div class="booking-card">
          <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:1rem">
            <div style="width:42px;height:42px;border-radius:12px;background:#f0fdf4;color:#22c55e;display:flex;align-items:center;justify-content:center;font-size:1.2rem">
              <i class="fa-solid fa-car-side"></i>
            </div>
            <div>
              <p style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.6px;color:#94a3b8">Phương tiện di chuyển</p>
              <p style="font-size:.95rem;font-weight:800;color:#0f172a">${transport.type}</p>
            </div>
          </div>
          <p style="font-size:.875rem;color:#64748b;margin-bottom:.5rem">📞 ${transport.provider_info || ''}</p>
          <p style="font-size:1.1rem;font-weight:800;color:#0d9488">${transport.price_estimate || ''}</p>
          <p style="font-size:.82rem;color:#94a3b8;margin-top:.5rem;font-style:italic">${transport.description || ''}</p>
        </div>`;
    }
  } else {
    bookingGrid.classList.add('hidden');
  }

  // ---- Itinerary Timeline ----
  const container = document.getElementById('itineraryContent');
  container.innerHTML = '';
  const itiList = state.final_translated?.translated_itinerary;

  if (Array.isArray(itiList) && itiList.length > 0) {
    itiList.forEach(day => {
      container.innerHTML += `
        <div class="timeline-item">
          <h4 class="timeline-day-title">${day.day_title}</h4>
          <div class="timeline-content">${(day.content || '').replace(/\n/g, '<br>')}</div>
        </div>`;
    });
  } else if (state.itinerary?.length > 0) {
    const byDay = {};
    state.itinerary.forEach(session => {
      const key = `Ngày ${session.day}`;
      if (!byDay[key]) byDay[key] = [];
      byDay[key].push(session);
    });
    Object.entries(byDay).forEach(([dayLabel, sessions]) => {
      const sessionsHtml = sessions.map(s => {
        const places = (s.places || []).map(p =>
          `<li style="margin-bottom:.4rem"><strong>${p.name}</strong> (${p.avg_duration}): ${p.description}</li>`
        ).join('');
        return `<div style="margin-bottom:.75rem">
          <p style="font-weight:700;color:#0d9488;margin-bottom:.35rem">🕐 Buổi ${s.session}</p>
          <ul style="list-style:none;padding-left:.5rem">${places || '<li style="color:#94a3b8">Chưa có địa điểm cụ thể</li>'}</ul>
        </div>`;
      }).join('');
      container.innerHTML += `
        <div class="timeline-item">
          <h4 class="timeline-day-title">${dayLabel}</h4>
          <div class="timeline-content">${sessionsHtml}</div>
        </div>`;
    });
  } else {
    container.innerHTML = '<p style="color:#94a3b8">Lịch trình trống — Vui lòng thử lại.</p>';
  }

  // ---- Food Suggestions ----
  const meals = state.food_suggestions?.meals;
  if (meals && meals.length > 0) {
    const foodSection = document.getElementById('foodSuggestionsSection');
    foodSection.classList.remove('hidden');
    document.getElementById('foodSuggestionsGrid').innerHTML = meals.map(m => `
      <div class="food-suggestion-card">
        <div style="font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#0d9488;margin-bottom:0.3rem">
          Ngày ${m.day} · Buổi ${m.session}
        </div>
        <div style="font-weight:700;color:#0f172a;margin-bottom:0.2rem">${m.restaurant_name}</div>
        <div style="font-size:0.82rem;color:#64748b;margin-bottom:0.35rem">⭐ ${m.specialty} · 📍 ${m.address || ''}</div>
        <div style="font-size:0.78rem;color:#0d9488;font-weight:600">${(m.avg_price_person || 0).toLocaleString('vi-VN')}₫/người</div>
        ${m.fallback_used ? '<div style="font-size:0.72rem;color:#f97316;margin-top:0.2rem">⚠️ Phương án dự phòng</div>' : ''}
      </div>
    `).join('');
  }

  // ---- Weather Alerts ----
  const weatherAlerts = state.weather?.alerts;
  if (weatherAlerts && weatherAlerts.length > 0) {
    const wSection = document.getElementById('weatherAlertSection');
    wSection.classList.remove('hidden');
    document.getElementById('weatherAlerts').innerHTML = weatherAlerts.map(a => `
      <div class="weather-alert-card">
        <strong>⚠️ Ngày ${a.day} · ${a.session} · ${a.place}</strong>
        <p style="margin-top:0.4rem;font-size:0.85rem;color:#374151">${a.warning}</p>
        ${a.alternative_activity ? `<p style="margin-top:0.4rem;font-size:0.82rem;color:#0d9488">💡 Gợi ý thay thế: ${a.alternative_activity}</p>` : ''}
      </div>
    `).join('');
  }

  document.getElementById('resultsContainer').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function downloadItinerary() {
  if (!App.rawItineraryData) return;
  const state = App.rawItineraryData;
  const dest = state.user_request?.destination || 'Quy Nhon';
  let content = `# Lịch trình du lịch ${dest}\n\n`;
  const itiList = state.final_translated?.translated_itinerary;
  if (Array.isArray(itiList)) {
    itiList.forEach(day => { content += `## ${day.day_title}\n${day.content}\n\n`; });
  } else {
    content += JSON.stringify(state.itinerary, null, 2);
  }
  const blob = new Blob([content], { type: 'text/plain; charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = `LichTrinh_${dest}.txt`;
  document.body.appendChild(a); a.click();
  document.body.removeChild(a); URL.revokeObjectURL(url);
}

// ============================================================
// AI CHAT
// ============================================================
function sendSuggestedChat(btn) {
  const langKey = `text${App.currentLang.charAt(0).toUpperCase() + App.currentLang.slice(1)}`;
  const text = btn.dataset[langKey] || btn.querySelector('span')?.textContent || '';
  document.getElementById('chatInput').value = text;
  sendChat();
}

async function sendChat() {
  if (App.isChatLoading) return;
  const input = document.getElementById('chatInput');
  const msg = input.value.trim();
  if (!msg) return;

  input.value = '';
  App.isChatLoading = true;
  document.getElementById('chatSendBtn').disabled = true;

  appendChatMessage(msg, 'user');
  const typingId = appendTypingIndicator();

  try {
    const resp = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg, language: App.currentLang })
    });
    const data = await resp.json();
    removeTypingIndicator(typingId);
    appendChatMessage(data.reply || 'Xin lỗi, không thể trả lời lúc này.', 'bot');
  } catch (e) {
    removeTypingIndicator(typingId);
    const errMsg = { vi:'Xin lỗi, server không phản hồi. Vui lòng thử lại!', en:'Sorry, server not responding. Please try again!', ja:'申し訳ありません、サーバーが応答していません。', ko:'죄송합니다, 서버가 응답하지 않습니다.' };
    appendChatMessage(errMsg[App.currentLang] || errMsg.vi, 'bot');
  }

  App.isChatLoading = false;
  document.getElementById('chatSendBtn').disabled = false;
}

function appendChatMessage(text, role) {
  const messages = document.getElementById('chatMessages');
  const now = new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });

  const div = document.createElement('div');
  div.className = `chat-msg ${role === 'bot' ? 'bot-msg' : 'user-msg'}`;

  if (role === 'bot') {
    div.innerHTML = `
      <div class="bot-avatar"><i class="fa-solid fa-robot"></i></div>
      <div class="msg-bubble">
        <p>${text.replace(/\n/g, '<br>')}</p>
        <span class="msg-time">${now}</span>
      </div>`;
  } else {
    div.innerHTML = `
      <div class="msg-bubble">
        <p>${text}</p>
        <span class="msg-time">${now}</span>
      </div>`;
  }
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
  return div;
}

function appendTypingIndicator() {
  const messages = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = 'chat-msg bot-msg';
  div.id = 'typingIndicator';
  div.innerHTML = `
    <div class="bot-avatar"><i class="fa-solid fa-robot"></i></div>
    <div class="msg-bubble">
      <div class="typing-dots">
        <span></span><span></span><span></span>
      </div>
    </div>`;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
  return 'typingIndicator';
}

function removeTypingIndicator(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

// ============================================================
// INIT
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
  initHeroSlideshow();
  initParticles();
  initNavbarScroll();
  applyTranslations();
  fetchWeather();
  fetchForecast();
  loadPlaces();

  // ESC close modal
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closePlaceModal();
  });

  // Smooth chat input for Enter
  document.getElementById('chatInput').addEventListener('keypress', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendChat(); }
  });
});
