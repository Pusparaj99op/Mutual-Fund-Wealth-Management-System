/**
 * FIMFP - Complete Multi-Language Translation System
 * Supports: English, Hindi, Marathi, Gujarati, Bengali
 */

const translations = {
    en: {
        // Header
        portalTitle: 'FIMFP',
        portalSubtitle: 'Federal Indian Mutual Fund Portal',
        portalSubtitleHindi: 'भारतीय संघीय म्यूचुअल फंड पोर्टल',
        digitalIndia: 'An Initiative of',
        digitalIndiaLogo: 'Digital India',

        // Navigation
        navHome: 'Home',
        navFunds: 'Browse Funds',
        navAnalysis: 'AI Analysis',
        navRecommend: 'Recommendations',
        navPortfolio: 'Portfolio',
        navCompare: 'Compare',
        navDashboard: 'Dashboard',
        navAdvanced: 'Advanced AI',

        // Hero Section
        govBadge: 'Government of India Initiative',
        heroTitle: 'AI-Powered Mutual Fund<br>Analysis & Recommendations',
        heroDesc: 'Make informed investment decisions with advanced AI/ML models including <strong>Monte Carlo Simulation</strong>, <strong>Black-Scholes</strong>, <strong>Black-Litterman</strong>, <strong>GARCH Volatility</strong>, and <strong>Machine Learning Predictors</strong>.',
        heroCTA1: 'Get AI Recommendations',
        heroCTA2: 'Browse All Funds',
        statFunds: 'Mutual Funds',
        statAMCs: 'AMCs',
        statModels: 'AI Models',
        statSimulations: 'Simulations',

        // Info Cards
        infoCard1Title: 'Monte Carlo Simulation',
        infoCard1Desc: '10,000 simulation paths using Geometric Brownian Motion for NAV prediction and VaR calculation.',
        infoCard2Title: 'Black-Scholes Model',
        infoCard2Desc: 'Greeks analysis (Delta, Gamma, Theta, Vega) and risk premium assessment.',
        infoCard3Title: 'Black-Litterman',
        infoCard3Desc: 'Portfolio optimization with market equilibrium and investor views integration.',
        infoCard4Title: 'ML Prediction Engine',
        infoCard4Desc: 'Ensemble learning with Random Forest and Gradient Boosting for return prediction.',

        // Notice
        noticeTitle: 'Important Notice:',
        noticeText: 'Mutual Fund investments are subject to market risks. Read all scheme related documents carefully before investing. Past performance is not indicative of future returns. This portal is for educational and informational purposes only.',

        // Browse Funds Section
        sectionBrowse: 'Browse Mutual Funds',
        sectionBrowseDesc: 'Explore and analyze 790+ mutual funds registered with SEBI',
        labelSearch: 'Search Fund / AMC',
        placeholderSearch: 'Enter scheme name or AMC...',
        labelCategory: 'Category',
        optAllCategories: 'All Categories',
        labelRisk: 'Risk Level',
        optAllRisk: 'All Risk Levels',
        riskVeryLow: '1 - Very Low',
        riskLow: '2 - Low',
        riskModerate: '3 - Moderate',
        riskHigh: '4 - High',
        riskVeryHigh: '5 - Very High',
        riskExtreme: '6 - Extremely High',
        labelRating: 'Min Rating',
        optAnyRating: 'Any Rating',
        btnSearch: 'Search',
        thSchemeName: 'Scheme Name',
        thAMC: 'AMC',
        thCategory: 'Category',
        thRating: 'Rating',
        th1YReturn: '1Y Return',
        th3YReturn: '3Y Return',
        thSharpe: 'Sharpe',
        thRisk: 'Risk',
        thActions: 'Actions',

        // AI Analysis Section
        sectionAnalysis: 'AI-Powered Analysis',
        sectionAnalysisDesc: 'Monte Carlo simulation and risk analysis for any mutual fund',
        cardAnalysisParams: 'Analysis Parameters',
        labelFundId: 'Fund ID',
        placeholderFundId: 'Enter Fund ID (1-790)',
        labelInvestment: 'Investment Amount (₹)',
        labelForecast: 'Forecast Horizon',
        opt1Month: '1 Month (30 days)',
        opt3Months: '3 Months (90 days)',
        opt6Months: '6 Months (180 days)',
        opt1Year: '1 Year (252 trading days)',
        opt2Years: '2 Years (504 days)',
        opt3Years: '3 Years (756 days)',
        btnRunSimulation: 'Run Monte Carlo Simulation',
        cardResults: 'Analysis Results',
        emptyAnalysis: 'Enter parameters and run simulation to view AI prediction results',
        cardMonteCarloChart: 'Monte Carlo Simulation Paths (Sample of 10,000)',

        // Recommendations Section
        sectionRecommend: 'AI Fund Recommendations',
        sectionRecommendDesc: 'Personalized fund suggestions based on your risk profile and investment goals',
        cardInvestProfile: 'Your Investment Profile',
        labelAge: 'Your Age (Years)',
        labelIncome: 'Annual Income (₹ Lakhs)',
        labelHorizon: 'Investment Horizon',
        opt1YearShort: '1 Year (Short-term)',
        opt3YearsMed: '3 Years (Medium-term)',
        opt5YearsLong: '5 Years (Long-term)',
        opt7Years: '7 Years',
        opt10YearsVLong: '10+ Years (Very Long-term)',
        labelLossTolerance: 'Loss Tolerance Level',
        optLossVeryLow: 'Very Low - Cannot accept any loss',
        optLossLow: 'Low - Can tolerate up to 10% loss',
        optLossMod: 'Moderate - Can tolerate up to 20% loss',
        optLossHigh: 'High - Can tolerate up to 30% loss',
        optLossVeryHigh: 'Very High - Can tolerate 30%+ loss',
        labelExperience: 'Investment Experience',
        optExpBeginner: 'Beginner - New to investing',
        optExpBasic: 'Basic - Some experience',
        optExpIntermed: 'Intermediate - Few years experience',
        optExpAdvanced: 'Advanced - Experienced investor',
        optExpExpert: 'Expert - Professional trader',
        labelInvestAmount: 'Investment Amount (₹)',
        btnGetRecommend: 'Get AI Recommendations',
        cardRiskProfile: 'Your Risk Profile',
        cardTopFunds: 'Top Recommended Funds Based on Your Profile',

        // Portfolio Optimizer
        sectionPortfolio: 'Portfolio Optimizer',
        sectionPortfolioDesc: 'Black-Litterman model for optimal asset allocation',
        cardSelectFunds: 'Select Funds for Optimization',
        cardSelectDesc: 'Enter fund IDs to include in your portfolio (comma-separated)',
        labelFundIds: 'Fund IDs (e.g., 1, 50, 100, 200)',
        labelTotalInvest: 'Total Investment Amount (₹)',
        btnOptimize: 'Optimize Portfolio',
        cardOptimalAlloc: 'Optimal Portfolio Allocation',
        cardAllocBreakdown: 'Allocation Breakdown',
        cardEfficientFrontier: 'Efficient Frontier',

        // Analytics Dashboard
        sectionDashboard: 'Market Analytics Dashboard',
        sectionDashboardDesc: 'Comprehensive market overview and fund statistics',
        cardDistribution: 'Fund Distribution by Category',
        cardAvgReturns: 'Average Returns by Category',

        // Advanced AI
        sectionAdvanced: 'Advanced AI/ML Analytics',
        sectionAdvancedDesc: 'Extended AI models: GARCH, Momentum, Factor Analysis, ML Predictions',
        cardAdvTools: 'Advanced Analysis Tools',
        labelAnalysisType: 'Analysis Type',
        optMLPrediction: 'ML Return Prediction',
        optMomentum: 'Momentum Analysis',
        optFactor: 'Factor Model Analysis',
        optSentiment: 'Market Sentiment',
        optComplete: 'Complete Analysis',
        btnRunAdvanced: 'Run Advanced Analysis',
        cardAdvResults: 'Analysis Results',
        emptyAdvanced: 'Select an analysis type and run to view AI/ML results',
        availableModels: 'Available AI Models:',

        // Footer
        aboutTitle: 'About FIMFP',
        aboutText: 'Federal Indian Mutual Fund Portal is an AI-powered investment analysis platform developed under the Digital India Programme. Content is sourced from AMFI and SEBI regulated mutual funds.',
        quickLinks: 'Quick Links',
        importantLinks: 'Important Links',
        linkSEBI: 'Securities and Exchange Board of India',
        linkAMFI: 'Association of Mutual Funds in India',
        linkRBI: 'Reserve Bank of India',
        linkNPI: 'National Portal of India',
        disclaimer: 'Disclaimer',
        disclaimerText: 'Mutual Fund investments are subject to market risks. Read all scheme related documents carefully before investing. Past performance is not indicative of future returns. This portal is developed for educational purposes only and should not be considered as financial advice.',
        footerCopyright: '© 2024 FIMFP - Federal Indian Mutual Fund Portal | Government of India',
        footerDeveloped: 'Designed & Developed under Digital India Programme by National Informatics Centre'
    },

    hi: {
        // Header
        portalTitle: 'FIMFP',
        portalSubtitle: 'भारतीय संघीय म्यूचुअल फंड पोर्टल',
        portalSubtitleHindi: 'Federal Indian Mutual Fund Portal',
        digitalIndia: 'एक पहल',
        digitalIndiaLogo: 'डिजिटल इंडिया',

        // Navigation
        navHome: 'होम',
        navFunds: 'फंड ब्राउज़ करें',
        navAnalysis: 'एआई विश्लेषण',
        navRecommend: 'सिफारिशें',
        navPortfolio: 'पोर्टफोलियो',
        navCompare: 'तुलना',
        navDashboard: 'डैशबोर्ड',
        navAdvanced: 'उन्नत एआई',

        // Hero Section
        govBadge: 'भारत सरकार की पहल',
        heroTitle: 'एआई-संचालित म्यूचुअल फंड<br>विश्लेषण और सिफारिशें',
        heroDesc: '<strong>मोंटे कार्लो सिमुलेशन</strong>, <strong>ब्लैक-शोल्स</strong>, <strong>ब्लैक-लिटरमैन</strong>, <strong>GARCH अस्थिरता</strong>, और <strong>मशीन लर्निंग प्रेडिक्टर्स</strong> सहित उन्नत एआई/एमएल मॉडल के साथ सूचित निवेश निर्णय लें।',
        heroCTA1: 'एआई सिफारिशें प्राप्त करें',
        heroCTA2: 'सभी फंड ब्राउज़ करें',
        statFunds: 'म्यूचुअल फंड्स',
        statAMCs: 'एएमसी',
        statModels: 'एआई मॉडल',
        statSimulations: 'सिमुलेशन',

        // Info Cards
        infoCard1Title: 'मोंटे कार्लो सिमुलेशन',
        infoCard1Desc: 'NAV भविष्यवाणी और VaR गणना के लिए ज्यामितीय ब्राउनियन मोशन का उपयोग करके 10,000 सिमुलेशन पथ।',
        infoCard2Title: 'ब्लैक-शोल्स मॉडल',
        infoCard2Desc: 'ग्रीक्स विश्लेषण (डेल्टा, गामा, थीटा, वेगा) और जोखिम प्रीमियम मूल्यांकन।',
        infoCard3Title: 'ब्लैक-लिटरमैन',
        infoCard3Desc: 'बाजार संतुलन और निवेशक विचारों के एकीकरण के साथ पोर्टफोलियो अनुकूलन।',
        infoCard4Title: 'एमएल प्रेडिक्शन इंजन',
        infoCard4Desc: 'रिटर्न भविष्यवाणी के लिए रैंडम फॉरेस्ट और ग्रेडिएंट बूस्टिंग के साथ एंसेंबल लर्निंग।',

        // Notice
        noticeTitle: 'महत्वपूर्ण सूचना:',
        noticeText: 'म्यूचुअल फंड निवेश बाजार जोखिमों के अधीन हैं। निवेश करने से पहले सभी योजना संबंधित दस्तावेजों को ध्यान से पढ़ें। पिछला प्रदर्शन भविष्य के रिटर्न का संकेत नहीं है। यह पोर्टल केवल शैक्षिक और सूचनात्मक उद्देश्यों के लिए है।',

        // Browse Funds Section
        sectionBrowse: 'म्यूचुअल फंड्स ब्राउज़ करें',
        sectionBrowseDesc: 'सेबी के साथ पंजीकृत 790+ म्यूचुअल फंड्स का अन्वेषण और विश्लेषण करें',
        labelSearch: 'फंड / एएमसी खोजें',
        placeholderSearch: 'योजना का नाम या एएमसी दर्ज करें...',
        labelCategory: 'श्रेणी',
        optAllCategories: 'सभी श्रेणियां',
        labelRisk: 'जोखिम स्तर',
        optAllRisk: 'सभी जोखिम स्तर',
        riskVeryLow: '1 - बहुत कम',
        riskLow: '2 - कम',
        riskModerate: '3 - मध्यम',
        riskHigh: '4 - उच्च',
        riskVeryHigh: '5 - बहुत उच्च',
        riskExtreme: '6 - अत्यंत उच्च',
        labelRating: 'न्यूनतम रेटिंग',
        optAnyRating: 'कोई भी रेटिंग',
        btnSearch: 'खोजें',
        thSchemeName: 'योजना का नाम',
        thAMC: 'एएमसी',
        thCategory: 'श्रेणी',
        thRating: 'रेटिंग',
        th1YReturn: '1 वर्ष रिटर्न',
        th3YReturn: '3 वर्ष रिटर्न',
        thSharpe: 'शार्प',
        thRisk: 'जोखिम',
        thActions: 'कार्रवाई',

        // AI Analysis Section
        sectionAnalysis: 'एआई-संचालित विश्लेषण',
        sectionAnalysisDesc: 'किसी भी म्यूचुअल फंड के लिए मोंटे कार्लो सिमुलेशन और जोखिम विश्लेषण',
        cardAnalysisParams: 'विश्लेषण पैरामीटर',
        labelFundId: 'फंड आईडी',
        placeholderFundId: 'फंड आईडी दर्ज करें (1-790)',
        labelInvestment: 'निवेश राशि (₹)',
        labelForecast: 'पूर्वानुमान अवधि',
        opt1Month: '1 महीना (30 दिन)',
        opt3Months: '3 महीने (90 दिन)',
        opt6Months: '6 महीने (180 दिन)',
        opt1Year: '1 वर्ष (252 ट्रेडिंग दिन)',
        opt2Years: '2 वर्ष (504 दिन)',
        opt3Years: '3 वर्ष (756 दिन)',
        btnRunSimulation: 'मोंटे कार्लो सिमुलेशन चलाएं',
        cardResults: 'विश्लेषण परिणाम',
        emptyAnalysis: 'एआई भविष्यवाणी परिणाम देखने के लिए पैरामीटर दर्ज करें और सिमुलेशन चलाएं',
        cardMonteCarloChart: 'मोंटे कार्लो सिमुलेशन पथ (10,000 का नमूना)',

        // Recommendations Section
        sectionRecommend: 'एआई फंड सिफारिशें',
        sectionRecommendDesc: 'आपकी जोखिम प्रोफ़ाइल और निवेश लक्ष्यों के आधार पर व्यक्तिगत फंड सुझाव',
        cardInvestProfile: 'आपकी निवेश प्रोफ़ाइल',
        labelAge: 'आपकी आयु (वर्ष)',
        labelIncome: 'वार्षिक आय (₹ लाख)',
        labelHorizon: 'निवेश अवधि',
        opt1YearShort: '1 वर्ष (अल्पकालिक)',
        opt3YearsMed: '3 वर्ष (मध्यम अवधि)',
        opt5YearsLong: '5 वर्ष (दीर्घकालिक)',
        opt7Years: '7 वर्ष',
        opt10YearsVLong: '10+ वर्ष (बहुत दीर्घकालिक)',
        labelLossTolerance: 'हानि सहनशीलता स्तर',
        optLossVeryLow: 'बहुत कम - कोई हानि स्वीकार नहीं',
        optLossLow: 'कम - 10% तक हानि सहन कर सकते हैं',
        optLossMod: 'मध्यम - 20% तक हानि सहन कर सकते हैं',
        optLossHigh: 'उच्च - 30% तक हानि सहन कर सकते हैं',
        optLossVeryHigh: 'बहुत उच्च - 30%+ हानि सहन कर सकते हैं',
        labelExperience: 'निवेश अनुभव',
        optExpBeginner: 'शुरुआती - निवेश में नए',
        optExpBasic: 'बुनियादी - कुछ अनुभव',
        optExpIntermed: 'मध्यवर्ती - कुछ वर्षों का अनुभव',
        optExpAdvanced: 'उन्नत - अनुभवी निवेशक',
        optExpExpert: 'विशेषज्ञ - पेशेवर ट्रेडर',
        labelInvestAmount: 'निवेश राशि (₹)',
        btnGetRecommend: 'एआई सिफारिशें प्राप्त करें',
        cardRiskProfile: 'आपकी जोखिम प्रोफ़ाइल',
        cardTopFunds: 'आपकी प्रोफ़ाइल के आधार पर शीर्ष अनुशंसित फंड',

        // Portfolio Optimizer
        sectionPortfolio: 'पोर्टफोलियो अनुकूलक',
        sectionPortfolioDesc: 'इष्टतम संपत्ति आवंटन के लिए ब्लैक-लिटरमैन मॉडल',
        cardSelectFunds: 'अनुकूलन के लिए फंड चुनें',
        cardSelectDesc: 'अपने पोर्टफोलियो में शामिल करने के लिए फंड आईडी दर्ज करें (कॉमा से अलग)',
        labelFundIds: 'फंड आईडी (उदा., 1, 50, 100, 200)',
        labelTotalInvest: 'कुल निवेश राशि (₹)',
        btnOptimize: 'पोर्टफोलियो अनुकूलित करें',
        cardOptimalAlloc: 'इष्टतम पोर्टफोलियो आवंटन',
        cardAllocBreakdown: 'आवंटन विवरण',
        cardEfficientFrontier: 'कुशल फ्रंटियर',

        // Analytics Dashboard
        sectionDashboard: 'बाजार विश्लेषण डैशबोर्ड',
        sectionDashboardDesc: 'व्यापक बाजार अवलोकन और फंड आंकड़े',
        cardDistribution: 'श्रेणी के अनुसार फंड वितरण',
        cardAvgReturns: 'श्रेणी के अनुसार औसत रिटर्न',

        // Advanced AI
        sectionAdvanced: 'उन्नत एआई/एमएल विश्लेषण',
        sectionAdvancedDesc: 'विस्तारित एआई मॉडल: GARCH, मोमेंटम, फैक्टर विश्लेषण, एमएल भविष्यवाणी',
        cardAdvTools: 'उन्नत विश्लेषण उपकरण',
        labelAnalysisType: 'विश्लेषण प्रकार',
        optMLPrediction: 'एमएल रिटर्न भविष्यवाणी',
        optMomentum: 'मोमेंटम विश्लेषण',
        optFactor: 'फैक्टर मॉडल विश्लेषण',
        optSentiment: 'बाजार भावना',
        optComplete: 'पूर्ण विश्लेषण',
        btnRunAdvanced: 'उन्नत विश्लेषण चलाएं',
        cardAdvResults: 'विश्लेषण परिणाम',
        emptyAdvanced: 'एआई/एमएल परिणाम देखने के लिए विश्लेषण प्रकार चुनें और चलाएं',
        availableModels: 'उपलब्ध एआई मॉडल:',

        // Footer
        aboutTitle: 'FIMFP के बारे में',
        aboutText: 'भारतीय संघीय म्यूचुअल फंड पोर्टल डिजिटल इंडिया कार्यक्रम के तहत विकसित एक एआई-संचालित निवेश विश्लेषण मंच है। सामग्री AMFI और SEBI विनियमित म्यूचुअल फंडों से प्राप्त होती है।',
        quickLinks: 'त्वरित लिंक',
        importantLinks: 'महत्वपूर्ण लिंक',
        linkSEBI: 'भारतीय प्रतिभूति और विनिमय बोर्ड',
        linkAMFI: 'भारत में म्यूचुअल फंड संघ',
        linkRBI: 'भारतीय रिजर्व बैंक',
        linkNPI: 'भारत का राष्ट्रीय पोर्टल',
        disclaimer: 'अस्वीकरण',
        disclaimerText: 'म्यूचुअल फंड निवेश बाजार जोखिमों के अधीन हैं। निवेश करने से पहले सभी योजना संबंधित दस्तावेजों को ध्यान से पढ़ें। पिछला प्रदर्शन भविष्य के रिटर्न का संकेत नहीं है। यह पोर्टल केवल शैक्षिक उद्देश्यों के लिए विकसित किया गया है।',
        footerCopyright: '© 2024 FIMFP - भारतीय संघीय म्यूचुअल फंड पोर्टल | भारत सरकार',
        footerDeveloped: 'राष्ट्रीय सूचना विज्ञान केंद्र द्वारा डिजिटल इंडिया कार्यक्रम के तहत डिज़ाइन और विकसित'
    },

    mr: {
        portalTitle: 'FIMFP',
        portalSubtitle: 'फेडरल इंडियन म्युच्युअल फंड पोर्टल',
        portalSubtitleHindi: 'Federal Indian Mutual Fund Portal',
        digitalIndia: 'या उपक्रमाचा',
        digitalIndiaLogo: 'डिजिटल इंडिया',
        navHome: 'होम',
        navFunds: 'फंड ब्राउझ करा',
        navAnalysis: 'एआय विश्लेषण',
        navRecommend: 'शिफारसी',
        navPortfolio: 'पोर्टफोलिओ',
        navCompare: 'तुलना',
        navDashboard: 'डॅशबोर्ड',
        navAdvanced: 'प्रगत एआय',
        govBadge: 'भारत सरकारचा उपक्रम',
        heroTitle: 'एआय-संचालित म्युच्युअल फंड<br>विश्लेषण आणि शिफारसी',
        heroDesc: 'प्रगत एआय/एमएल मॉडेल्ससह माहितीपूर्ण गुंतवणूक निर्णय घ्या',
        heroCTA1: 'एआय शिफारसी मिळवा',
        heroCTA2: 'सर्व फंड ब्राउझ करा',
        statFunds: 'म्युच्युअल फंड',
        statAMCs: 'एएमसी',
        statModels: 'एआय मॉडेल्स',
        statSimulations: 'सिम्युलेशन',
        infoCard1Title: 'मॉन्टे कार्लो सिम्युलेशन',
        infoCard1Desc: 'NAV अंदाज आणि VaR गणनेसाठी 10,000 सिम्युलेशन मार्ग',
        infoCard2Title: 'ब्लॅक-शोल्स मॉडेल',
        infoCard2Desc: 'ग्रीक्स विश्लेषण आणि जोखीम प्रीमियम मूल्यांकन',
        infoCard3Title: 'ब्लॅक-लिटरमन',
        infoCard3Desc: 'बाजार समतोल आणि गुंतवणूकदार दृश्यांसह पोर्टफोलिओ ऑप्टिमायझेशन',
        infoCard4Title: 'एमएल प्रेडिक्शन इंजिन',
        infoCard4Desc: 'रिटर्न अंदाजासाठी रँडम फॉरेस्ट आणि ग्रेडियंट बूस्टिंग',
        noticeTitle: 'महत्त्वाची सूचना:',
        noticeText: 'म्युच्युअल फंड गुंतवणूक बाजार जोखमींच्या अधीन आहेत। गुंतवणूक करण्यापूर्वी सर्व योजना संबंधित कागदपत्रे काळजीपूर्वक वाचा।',
        sectionBrowse: 'म्युच्युअल फंड ब्राउझ करा',
        sectionBrowseDesc: 'सेबीमध्ये नोंदणीकृत 790+ म्युच्युअल फंडांचा शोध घ्या',
        labelSearch: 'फंड / एएमसी शोधा',
        btnSearch: 'शोधा',
        sectionAnalysis: 'एआय-संचालित विश्लेषण',
        sectionAnalysisDesc: 'कोणत्याही म्युच्युअल फंडसाठी मॉन्टे कार्लो सिम्युलेशन',
        btnRunSimulation: 'मॉन्टे कार्लो सिम्युलेशन चालवा',
        sectionRecommend: 'एआय फंड शिफारसी',
        sectionRecommendDesc: 'तुमच्या जोखीम प्रोफाइलवर आधारित वैयक्तिक फंड सूचना',
        btnGetRecommend: 'एआय शिफारसी मिळवा',
        sectionPortfolio: 'पोर्टफोलिओ ऑप्टिमायझर',
        sectionPortfolioDesc: 'इष्टतम एसेट अलोकेशनसाठी ब्लॅक-लिटरमन मॉडेल',
        btnOptimize: 'पोर्टफोलिओ ऑप्टिमाइझ करा',
        sectionDashboard: 'बाजार विश्लेषण डॅशबोर्ड',
        sectionDashboardDesc: 'सर्वसमावेशक बाजार आढावा आणि फंड आकडेवारी',
        sectionAdvanced: 'प्रगत एआय/एमएल विश्लेषण',
        sectionAdvancedDesc: 'विस्तारित एआय मॉडेल्स: GARCH, मोमेंटम, फॅक्टर विश्लेषण',
        btnRunAdvanced: 'प्रगत विश्लेषण चालवा',
        aboutTitle: 'FIMFP बद्दल',
        quickLinks: 'द्रुत दुवे',
        importantLinks: 'महत्त्वाचे दुवे',
        disclaimer: 'अस्वीकरण',
        footerCopyright: '© 2024 FIMFP - फेडरल इंडियन म्युच्युअल फंड पोर्टल | भारत सरकार'
    },

    gu: {
        portalTitle: 'FIMFP',
        portalSubtitle: 'ફેડરલ ઇન્ડિયન મ્યુચ્યુઅલ ફંડ પોર્ટલ',
        portalSubtitleHindi: 'Federal Indian Mutual Fund Portal',
        digitalIndia: 'ની પહેલ',
        digitalIndiaLogo: 'ડિજિટલ ઇન્ડિયા',
        navHome: 'હોમ',
        navFunds: 'ફંડ્સ બ્રાઉઝ કરો',
        navAnalysis: 'એઆઈ વિશ્લેષણ',
        navRecommend: 'ભલામણો',
        navPortfolio: 'પોર્ટફોલિયો',
        navCompare: 'સરખામણી',
        navDashboard: 'ડેશબોર્ડ',
        navAdvanced: 'એડવાન્સ એઆઈ',
        govBadge: 'ભારત સરકારની પહેલ',
        heroTitle: 'એઆઈ-સંચાલિત મ્યુચ્યુઅલ ફંડ<br>વિશ્લેષણ અને ભલામણો',
        heroDesc: 'અદ્યતન એઆઈ/એમએલ મોડલ્સ સાથે માહિતગાર રોકાણ નિર્ણયો લો',
        heroCTA1: 'એઆઈ ભલામણો મેળવો',
        heroCTA2: 'બધા ફંડ્સ બ્રાઉઝ કરો',
        statFunds: 'મ્યુચ્યુઅલ ફંડ્સ',
        statAMCs: 'એએમસી',
        statModels: 'એઆઈ મોડલ્સ',
        statSimulations: 'સિમ્યુલેશન',
        infoCard1Title: 'મોન્ટે કાર્લો સિમ્યુલેશન',
        infoCard1Desc: 'NAV આગાહી માટે 10,000 સિમ્યુલેશન પાથ',
        infoCard2Title: 'બ્લેક-શોલ્સ મોડલ',
        infoCard2Desc: 'ગ્રીક્સ વિશ્લેષણ અને જોખમ પ્રીમિયમ મૂલ્યાંકન',
        infoCard3Title: 'બ્લેક-લિટરમેન',
        infoCard3Desc: 'બજાર સંતુલન સાથે પોર્ટફોલિયો ઓપ્ટિમાઇઝેશન',
        infoCard4Title: 'એમએલ પ્રેડિક્શન એન્જિન',
        infoCard4Desc: 'રિટર્ન આગાહી માટે એન્સેમ્બલ લર્નિંગ',
        noticeTitle: 'મહત્વપૂર્ણ સૂચના:',
        noticeText: 'મ્યુચ્યુઅલ ફંડ રોકાણો બજાર જોખમોને આધિન છે। રોકાણ કરતા પહેલા બધા દસ્તાવેજો કાળજીપૂર્વક વાંચો।',
        sectionBrowse: 'મ્યુચ્યુઅલ ફંડ્સ બ્રાઉઝ કરો',
        sectionBrowseDesc: 'સેબી સાથે નોંધાયેલા 790+ ફંડ્સનું અન્વેષણ કરો',
        btnSearch: 'શોધો',
        sectionAnalysis: 'એઆઈ-સંચાલિત વિશ્લેષણ',
        btnRunSimulation: 'મોન્ટે કાર્લો સિમ્યુલેશન ચલાવો',
        sectionRecommend: 'એઆઈ ફંડ ભલામણો',
        btnGetRecommend: 'એઆઈ ભલામણો મેળવો',
        sectionPortfolio: 'પોર્ટફોલિયો ઓપ્ટિમાઇઝર',
        btnOptimize: 'પોર્ટફોલિયો ઓપ્ટિમાઇઝ કરો',
        sectionDashboard: 'બજાર વિશ્લેષણ ડેશબોર્ડ',
        sectionAdvanced: 'એડવાન્સ એઆઈ/એમએલ વિશ્લેષણ',
        btnRunAdvanced: 'એડવાન્સ વિશ્લેષણ ચલાવો',
        aboutTitle: 'FIMFP વિશે',
        quickLinks: 'ઝડપી લિંક્સ',
        importantLinks: 'મહત્વપૂર્ણ લિંક્સ',
        disclaimer: 'અસ્વીકરણ',
        footerCopyright: '© 2024 FIMFP - ફેડરલ ઇન્ડિયન મ્યુચ્યુઅલ ફંડ પોર્ટલ | ભારત સરકાર'
    },

    bn: {
        portalTitle: 'FIMFP',
        portalSubtitle: 'ফেডারেল ইন্ডিয়ান মিউচুয়াল ফান্ড পোর্টাল',
        portalSubtitleHindi: 'Federal Indian Mutual Fund Portal',
        digitalIndia: 'এর উদ্যোগ',
        digitalIndiaLogo: 'ডিজিটাল ইন্ডিয়া',
        navHome: 'হোম',
        navFunds: 'ফান্ড ব্রাউজ করুন',
        navAnalysis: 'এআই বিশ্লেষণ',
        navRecommend: 'সুপারিশ',
        navPortfolio: 'পোর্টফোলিও',
        navCompare: 'তুলনা',
        navDashboard: 'ড্যাশবোর্ড',
        navAdvanced: 'উন্নত এআই',
        govBadge: 'ভারত সরকারের উদ্যোগ',
        heroTitle: 'এআই-চালিত মিউচুয়াল ফান্ড<br>বিশ্লেষণ এবং সুপারিশ',
        heroDesc: 'উন্নত এআই/এমএল মডেলগুলির সাথে জ্ঞাত বিনিয়োগ সিদ্ধান্ত নিন',
        heroCTA1: 'এআই সুপারিশ পান',
        heroCTA2: 'সমস্ত ফান্ড ব্রাউজ করুন',
        statFunds: 'মিউচুয়াল ফান্ড',
        statAMCs: 'এএমসি',
        statModels: 'এআই মডেল',
        statSimulations: 'সিমুলেশন',
        infoCard1Title: 'মন্টে কার্লো সিমুলেশন',
        infoCard1Desc: 'NAV পূর্বাভাসের জন্য 10,000 সিমুলেশন পথ',
        infoCard2Title: 'ব্ল্যাক-শোলস মডেল',
        infoCard2Desc: 'গ্রীক্স বিশ্লেষণ এবং ঝুঁকি প্রিমিয়াম মূল্যায়ন',
        infoCard3Title: 'ব্ল্যাক-লিটারম্যান',
        infoCard3Desc: 'বাজার ভারসাম্যের সাথে পোর্টফোলিও অপ্টিমাইজেশন',
        infoCard4Title: 'এমএল প্রেডিকশন ইঞ্জিন',
        infoCard4Desc: 'রিটার্ন পূর্বাভাসের জন্য এনসেম্বল লার্নিং',
        noticeTitle: 'গুরুত্বপূর্ণ বিজ্ঞপ্তি:',
        noticeText: 'মিউচুয়াল ফান্ড বিনিয়োগ বাজার ঝুঁকির সাপেক্ষে। বিনিয়োগ করার আগে সমস্ত নথি সাবধানে পড়ুন।',
        sectionBrowse: 'মিউচুয়াল ফান্ড ব্রাউজ করুন',
        sectionBrowseDesc: 'সেবিতে নিবন্ধিত 790+ ফান্ড অন্বেষণ করুন',
        btnSearch: 'অনুসন্ধান',
        sectionAnalysis: 'এআই-চালিত বিশ্লেষণ',
        btnRunSimulation: 'মন্টে কার্লো সিমুলেশন চালান',
        sectionRecommend: 'এআই ফান্ড সুপারিশ',
        btnGetRecommend: 'এআই সুপারিশ পান',
        sectionPortfolio: 'পোর্টফোলিও অপ্টিমাইজার',
        btnOptimize: 'পোর্টফোলিও অপ্টিমাইজ করুন',
        sectionDashboard: 'বাজার বিশ্লেষণ ড্যাশবোর্ড',
        sectionAdvanced: 'উন্নত এআই/এমএল বিশ্লেষণ',
        btnRunAdvanced: 'উন্নত বিশ্লেষণ চালান',
        aboutTitle: 'FIMFP সম্পর্কে',
        quickLinks: 'দ্রুত লিঙ্ক',
        importantLinks: 'গুরুত্বপূর্ণ লিঙ্ক',
        disclaimer: 'দাবিত্যাগ',
        footerCopyright: '© 2024 FIMFP - ফেডারেল ইন্ডিয়ান মিউচুয়াল ফান্ড পোর্টাল | ভারত সরকার'
    }
};

let currentLanguage = 'en';

function t(key) {
    return translations[currentLanguage][key] || translations.en[key] || key;
}

function switchLanguage(lang) {
    currentLanguage = lang;
    localStorage.setItem('fimfp_language', lang);
    document.documentElement.lang = lang;
    updatePageContent();
    updateLanguageButtons();
}

function updatePageContent() {
    // Header
    document.querySelector('.portal-subtitle').textContent = t('portalSubtitle');
    document.querySelector('.portal-subtitle-hindi').textContent = t('portalSubtitleHindi');
    document.querySelector('.di-text').textContent = t('digitalIndia');

    // Navigation
    const navLinks = document.querySelectorAll('.nav-link');
    const navKeys = ['navHome', 'navFunds', 'navAnalysis', 'navRecommend', 'navPortfolio', 'navCompare', 'navDashboard', 'navAdvanced'];
    navLinks.forEach((link, i) => { if (navKeys[i]) link.textContent = t(navKeys[i]); });

    // Hero Section
    const heroBadge = document.querySelector('.hero-badge');
    if (heroBadge) heroBadge.innerHTML = '🏛️ ' + t('govBadge');
    const heroTitle = document.querySelector('.hero-title');
    if (heroTitle) heroTitle.innerHTML = t('heroTitle');
    const heroDesc = document.querySelector('.hero-description');
    if (heroDesc) heroDesc.innerHTML = t('heroDesc');

    const heroButtons = document.querySelectorAll('.hero-actions .btn');
    if (heroButtons[0]) heroButtons[0].textContent = t('heroCTA1');
    if (heroButtons[1]) heroButtons[1].textContent = t('heroCTA2');

    const statLabels = document.querySelectorAll('.stat-label');
    const statKeys = ['statFunds', 'statAMCs', 'statModels', 'statSimulations'];
    statLabels.forEach((label, i) => { if (statKeys[i]) label.textContent = t(statKeys[i]); });

    // Info Cards
    const infoCards = document.querySelectorAll('.info-card');
    const cardTitles = ['infoCard1Title', 'infoCard2Title', 'infoCard3Title', 'infoCard4Title'];
    const cardDescs = ['infoCard1Desc', 'infoCard2Desc', 'infoCard3Desc', 'infoCard4Desc'];
    infoCards.forEach((card, i) => {
        const h3 = card.querySelector('h3');
        const p = card.querySelector('p');
        if (h3 && cardTitles[i]) h3.textContent = t(cardTitles[i]);
        if (p && cardDescs[i]) p.textContent = t(cardDescs[i]);
    });

    // Notice
    const notice = document.querySelector('.gov-notice');
    if (notice) notice.innerHTML = '<strong>' + t('noticeTitle') + '</strong> ' + t('noticeText');

    // Section Titles
    updateSection('funds', 'sectionBrowse', 'sectionBrowseDesc');
    updateSection('predict', 'sectionAnalysis', 'sectionAnalysisDesc');
    updateSection('recommend', 'sectionRecommend', 'sectionRecommendDesc');
    updateSection('optimize', 'sectionPortfolio', 'sectionPortfolioDesc');
    updateSection('analytics', 'sectionDashboard', 'sectionDashboardDesc');
    updateSection('advanced', 'sectionAdvanced', 'sectionAdvancedDesc');

    // Buttons
    updateButton('[onclick="searchFunds()"]', 'btnSearch');
    updateButton('#predictionForm button[type="submit"]', 'btnRunSimulation');
    updateButton('#riskProfileForm button[type="submit"]', 'btnGetRecommend');
    updateButton('#optimizerForm button[type="submit"]', 'btnOptimize');
    updateButton('#advancedForm button[type="submit"]', 'btnRunAdvanced');

    // Footer
    const footerTitles = document.querySelectorAll('.footer-section h4');
    const footerKeys = ['aboutTitle', 'quickLinks', 'importantLinks', 'disclaimer'];
    footerTitles.forEach((title, i) => { if (footerKeys[i]) title.textContent = t(footerKeys[i]); });

    const footerBottom = document.querySelector('.footer-bottom');
    if (footerBottom) {
        const ps = footerBottom.querySelectorAll('p');
        if (ps[0]) ps[0].textContent = t('footerCopyright');
        if (ps[1] && translations[currentLanguage].footerDeveloped) ps[1].textContent = t('footerDeveloped');
    }
}

function updateSection(id, titleKey, descKey) {
    const section = document.getElementById(id);
    if (section) {
        const title = section.querySelector('.section-title');
        const subtitle = section.querySelector('.section-subtitle');
        if (title) title.innerHTML = t(titleKey);
        if (subtitle) subtitle.textContent = t(descKey);
    }
}

function updateButton(selector, key) {
    const btn = document.querySelector(selector);
    if (btn && translations[currentLanguage][key]) btn.textContent = t(key);
}

function updateLanguageButtons() {
    document.querySelectorAll('.lang-btn[data-lang]').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.lang === currentLanguage);
    });
}

document.addEventListener('DOMContentLoaded', function () {
    const savedLang = localStorage.getItem('fimfp_language');
    if (savedLang && translations[savedLang]) {
        currentLanguage = savedLang;
    }
    updatePageContent();
    updateLanguageButtons();
});

window.languageSystem = { switch: switchLanguage, current: () => currentLanguage, t: t };
