// ─── Constants ────────────────────────────────────────────────────

const BRAND_DOMAINS = {
  'Accor': 'accor.com',
  'Marriott International': 'marriotthotels.com',
  'Hilton Hotels & Resorts': 'hilton.com',
  'Hyatt Hotels Corporation': 'hyatt.com',
  'Four Seasons Hotels & Resorts': 'fourseasons.com',
  'Radisson Hotel Group': 'radissonhotels.com',
  'IHG Hotels & Resorts': 'ihg.com',
  'RIU Hotels & Resorts': 'riu.com',
  'Barceló Hotel Group': 'barcelo.com',
  'Kenzi Hotels Group': 'kenzi-hotels.com',
  'Atlas Hotels Group': 'almada.ma',
  'Atlas Hospitality Group': 'almada.ma',
  'View Hotels': 'almada.ma',
  'The View': 'almada.ma',
  'Terminus Hotels': 'almada.ma',
  'Mogador Hotels Group': 'hotelmogador.com',
  'Onomo Hotels': 'onomohotel.com',
  'Zalagh Hotels Group': 'zalagh.com',
  'Louvre Hotels Group': 'louvrehotels.com',
  'Wyndham Hotels & Resorts': 'wyndhamhotels.com',
  'Rotana Hotels': 'rotana.com',
  'Meininger Hotels': 'meininger-hotels.com',
  'Club Med': 'clubmed.com',
  'Iberostar Hotels & Resorts': 'iberostar.com',
  'Minor Hotels': 'minorhotels.com',
  'Pestana Hotel Group': 'pestana.com',
  'Barrière': 'hotelsbarriere.com',
  'Oberoi Hotels & Resorts': 'oberoihotels.com',
  'Nobu Hospitality': 'nobuhotels.com',
  'Relais & Châteaux': 'relaischateaux.com',
  'Farah Hotels': 'farahhotels.com',
  'TUI Hotels & Resorts': 'tui.com',
  'Globalia Hotels': 'beliveholidays.com',
  'Royal Mansour Collection': 'royalmansour.com',
  'Kerzner International': 'kerzner.com',
  'Groupe Barrière': 'hotelsbarriere.com',
  'Groupe Lucien Barrière': 'hotelsbarriere.com',
  'Aman Resorts': 'aman.com',
  'Mandarin Oriental Hotel Group': 'mandarinoriental.com',
  'Virgin Limited Edition': 'virginlimitededition.com',
  'Soho Boutique': 'sohohoteles.com',
  'Zephyr': 'zephyr.ma',
};

const LOCAL_BRAND_LOGOS = {
  'Mia Hotels': '/static/images/brands/mia-hotels.jpg',
  'Zephyr': '/static/images/brands/zephyr-logo.jpg',
};

const BRAND_CUSTOM_LOGOS = {
  'Zalagh Hotels Group':         { letter: 'Z',  bg: '#1A1A1A', color: '#B87860' },
  'Farah Hotels':                { letter: 'F',  bg: '#1A1A1A', color: '#B87860' },
  'Independent Ultra Luxury':    { letter: 'UL', bg: '#1A1A1A', color: '#C8A96E' },
  'Independent Luxury':          { letter: 'IL', bg: '#1A1A1A', color: '#B87860' },
  'Independent Upper Upscale':   { letter: 'UU', bg: '#1A1A1A', color: '#888888' },
  'Independent Upscale':         { letter: 'IU', bg: '#1A1A1A', color: '#666666' },
  'Independent Midscale':        { letter: 'IM', bg: '#1A1A1A', color: '#555555' },
  'Independent Economy':         { letter: 'IE', bg: '#1A1A1A', color: '#444444' },
  'Mia Hotels':                  { letter: 'M',  bg: '#1A1A1A', color: '#B87860' },
  'Story Hospitality':           { letter: 'S',  bg: '#1A1A1A', color: '#B87860' },
  'Zephyr':                      { letter: 'Z',  bg: '#1A1A1A', color: '#B87860' },
};

const BRAND_DESCRIPTIONS = {
  'Marriott International': "Marriott International is the world's largest hotel company with over 30 brands and 9,000 properties across 140 countries. In Morocco, Marriott operates through flagship brands including Marriott Hotels, Sheraton, Courtyard, Four Points, and the ultra-luxury St. Regis and Ritz-Carlton. The group has been present in Morocco since 1989 and continues to expand with confirmed pipeline projects in Marrakech and Tamuda Bay. Marriott's Morocco portfolio spans all segments from upper upscale business hotels in Casablanca and Rabat to luxury resort developments on the Atlantic and Mediterranean coasts.",
  'Hyatt Hotels Corporation': "Hyatt Hotels Corporation is a leading global hospitality company headquartered in Chicago, with a portfolio of over 20 brands across luxury, lifestyle, and select-service segments. In Morocco, Hyatt operates through Hyatt Regency, Park Hyatt, and Hyatt Place, with properties in Casablanca and the Taghazout Bay resort destination. The group entered Morocco in 1973 with the opening of Hyatt Regency Casablanca, one of the country's first international luxury hotel brands, and has since expanded into the emerging resort corridor of Agadir and Taghazout. Hyatt's Morocco strategy focuses on premium resort and urban business hotels targeting international corporate and leisure travelers.",
  'Accor': "Accor is Europe's largest hotel group and Morocco's dominant hospitality operator, with a portfolio spanning ultra-luxury to economy through brands including Sofitel, Fairmont, Pullman, Mövenpick, Novotel, Mercure, Ibis, and MGallery. In Morocco, Accor operates primarily through Risma, its listed subsidiary on the Casablanca Stock Exchange and the country's only publicly traded hotel company. Having been present in Morocco for over 50 years, Accor manages the largest branded hotel portfolio in the country by both number of properties and total keys. The group's footprint covers all major destinations from Casablanca and Marrakech to Agadir, Fes, Rabat, and Tanger, with continued expansion through new lifestyle brands including Mama Shelter and 25hours.",
  'Four Seasons Hotels & Resorts': "Four Seasons Hotels & Resorts is a Canadian luxury hospitality company operating over 120 properties in 50 countries, consistently ranked among the world's finest hotel brands. In Morocco, Four Seasons has established a significant presence with landmark properties in Casablanca, Marrakech, and the newly opened Rabat at Kasr Al Bahr, reflecting the brand's confidence in Morocco's luxury tourism potential. Each Four Seasons property in Morocco is positioned at the very top of its local market, offering bespoke service standards and prime real estate locations that set the benchmark for ultra-luxury hospitality in the country. The brand's continued investment in Morocco aligns with the kingdom's Vision 2030 tourism ambitions and the growing appetite from high-net-worth international travelers.",
  'Radisson Hotel Group': "Radisson Hotel Group is a Belgian-based multinational hospitality company operating over 1,700 hotels across 120 countries through brands including Radisson Blu, Radisson, Radisson RED, and Park Inn. In Morocco, Radisson has emerged as one of the most active international operators, with a rapidly expanding portfolio spanning Casablanca, Marrakech, Fes, Al Hoceima, Saidia, and the Taghazout Bay resort corridor. The group's Morocco strategy combines full-service Radisson Blu properties in major urban and resort destinations with the newer Radisson Residences concept targeting the branded residential segment. Radisson's aggressive expansion in Morocco reflects its broader Africa and Middle East growth strategy and its early recognition of Morocco's emerging status as a premium tourism and investment destination.",
  'IHG Hotels & Resorts': "IHG Hotels & Resorts is a British multinational hospitality company headquartered in Windsor, operating over 6,000 hotels across nearly 100 countries through brands including InterContinental, Crowne Plaza, Holiday Inn, and voco. In Morocco, IHG maintains a selective presence focused on the upper upscale and luxury segments, with its properties serving primarily the corporate and MICE travel segments in major business destinations. The group's Morocco footprint reflects a measured approach to a market it views as strategically important given the country's growing role as a regional business hub and international conference destination. IHG's global distribution network and loyalty program provide its Morocco properties with strong connectivity to international corporate accounts and premium leisure travelers.",
  'RIU Hotels & Resorts': "RIU Hotels & Resorts is a Spanish family-owned hotel group founded in 1953 and one of Europe's leading all-inclusive resort operators, with over 100 properties across 20 countries. In Morocco, RIU has built the country's largest beach resort portfolio with six properties concentrated in Agadir and Marrakech, representing a significant share of Morocco's international leisure tourism capacity. The group's Tikida brand operates a cluster of all-inclusive resorts in Agadir that have been foundational to the city's development as a mass-market European beach destination, while the newer Riu Palace Tikida Taghazout positions the group in the premium resort segment. RIU's long-standing commitment to Morocco and its large room count make it one of the most influential operators in the country's leisure tourism ecosystem.",
  'Hilton Hotels & Resorts': "Hilton Hotels & Resorts is one of the world's most recognized hospitality brands, part of the Hilton portfolio of 22 brands operating over 7,000 properties across 123 countries. In Morocco, Hilton has built a diversified portfolio spanning its full-service Hilton brand, Hilton Garden Inn, DoubleTree, Conrad, and the ultra-luxury Waldorf Astoria, with properties across Casablanca, Tanger, Rabat, and the Taghazout Bay resort destination. The group's Morocco expansion has accelerated significantly in recent years, with major openings in Tanger and the Taghazout Bay surf village reinforcing Hilton's commitment to the country's growing tourism infrastructure. The recently opened Waldorf Astoria Rabat Salé represents Hilton's most prestigious Morocco asset and signals the group's confidence in the capital's luxury hospitality potential.",
  'Barceló Hotel Group': "Barceló Hotel Group is a Spanish family-owned hospitality company founded in 1931, operating over 270 hotels across 24 countries through brands including Barceló Hotels, Royal Hideaway, and Occidental. In Morocco, Barceló has assembled one of the largest international operator portfolios in the country with properties spanning Casablanca, Fes, and Tanger, reflecting the group's long-standing strategic interest in the Moroccan market. The group's flagship Royal Hideaway Casablanca positions Barceló at the top of the luxury segment in the economic capital, while the recently rebranded Hotel Borj Rabat expands its presence into the administrative capital. Barceló's deep roots in Spanish-speaking markets and its established relationships with European tour operators make it a natural bridge between Morocco's traditional European feeder markets and its growing international ambitions.",
  'Kenzi Hotels Group': "Kenzi Hotels Group is Morocco's largest home-grown hotel chain, with a portfolio of upper upscale and luxury properties operating exclusively within the kingdom. Founded in the 1970s and headquartered in Casablanca, Kenzi has built an iconic presence in Morocco's key destinations including Casablanca, Marrakech, Tanger, and Ouarzazate, with properties that have defined the upper upscale segment in their respective markets for decades. The Kenzi Tower Hotel in Casablanca and the Kenzi Menara Palace in Marrakech are among the most recognized hotel addresses in Morocco, serving a loyal base of domestic corporate clients and international leisure travelers. As one of the few large-scale independent Moroccan hotel groups, Kenzi represents an important counterweight to international brands and a significant part of the country's hospitality heritage.",
  'Club Med': "Club Med is a French pioneering all-inclusive resort company founded in 1950, credited with creating the modern all-inclusive holiday concept and operating over 70 resorts across 26 countries. In Morocco, Club Med has a historic presence dating back to 1966 with the opening of Club Med Marrakech La Palmeraie, one of the group's earliest properties globally, followed by Club Med Yasmina on the Mediterranean coast of Al Hoceima. The two Moroccan resorts serve primarily European leisure travelers seeking a premium all-inclusive experience in culturally rich destinations, contributing meaningfully to Morocco's international leisure tourism arrivals. Club Med's long relationship with Morocco reflects the country's enduring appeal as a European holiday destination and its unique positioning at the intersection of European comfort and North African cultural immersion.",
  'Iberostar Hotels & Resorts': "Iberostar Hotels & Resorts is a Spanish family-owned hotel group founded in 1986 and one of Europe's leading beach resort operators, with over 100 properties across 16 countries. In Morocco, Iberostar operates three Waves-branded properties in Agadir, Marrakech, and Saidia, positioning the group firmly in the upscale all-inclusive beach and resort segment. The Iberostar Waves concept targets European sun-and-sea travelers seeking a modern all-inclusive experience with a strong sustainability focus, reflecting the group's global Responsible Tourism commitment. Iberostar's Morocco portfolio plays a meaningful role in the country's leisure tourism infrastructure, particularly in the Agadir and Saidia resort corridors that depend heavily on European charter and package travel.",
  'Royal Mansour Collection': "Royal Mansour Collection is a Moroccan ultra-luxury hospitality brand operating the kingdom's most prestigious and exclusive hotel addresses. The collection currently comprises three iconic properties including the Royal Mansour Marrakech, widely regarded as one of the finest hotels in the world, the Royal Mansour Casablanca, and the Royal Mansour Tamuda Bay on the Mediterranean coast. Each property is distinguished by extraordinary architectural craftsmanship, bespoke personalised service, and an unwavering commitment to celebrating Moroccan art, culture, and gastronomy at the highest level. The Royal Mansour Collection represents Morocco's most powerful statement of indigenous luxury hospitality and serves as a benchmark for international ultra-luxury standards within the kingdom.",
  'Mogador Hotels Group': "Mogador Hotels Group is a Moroccan independent hotel chain founded in Marrakech, operating a portfolio of upper upscale properties concentrated in the kingdom's key leisure and business destinations. The group has built a strong presence in Marrakech where it operates four complementary properties including the Grand Mogador Agdal, Grand Mogador Menara, Grand Mogador Aqua Resort, and Mogador Menzah Appart Hotel, making it one of the city's most significant independent hotel operators by total room count. Mogador's expansion to Tanger with the Grand Mogador Sea View further demonstrates the group's ambition to establish a national footprint beyond its Marrakech origins. As an independently owned Moroccan brand serving both domestic and international guests, Mogador Hotels represents an important part of the country's locally rooted hospitality sector.",
  'Onomo Hotels': "Onomo Hotels is an African hospitality brand founded in 2010 and headquartered in Dakar, Senegal, specializing in modern upscale and midscale hotels tailored to the African business and leisure traveler. In Morocco, Onomo operates one of its largest national portfolios with properties in Casablanca's city center, airport, and Sidi Maarouf districts, as well as in Rabat, reflecting the brand's focus on Morocco's primary business destinations. The group's Le Square by Onomo Collection positions the brand in the upper upscale lifestyle segment, demonstrating Onomo's ambition to move beyond its midscale origins into more premium territory. As a pan-African brand with deep roots in francophone Africa, Onomo brings a uniquely African perspective to Morocco's hospitality market and serves a growing base of intra-African business travelers.",
  'Atlas Hospitality Group': "Atlas Hospitality Group is a Moroccan conglomerate operating in hospitality, real estate, and tourism under the Almada Group umbrella, with a hotel portfolio that includes the Atlas Hotels brand, The View luxury resorts, and the Terminus Hotels collection. The group's hospitality division operates properties across Morocco's major cities and resort destinations, offering a range of experiences from upscale urban hotels to premium leisure resorts. The View Rabat and The View Bouznika represent the group's most ambitious luxury positioning, combining contemporary design with premium resort amenities in locations between Rabat and Casablanca. As part of one of Morocco's most diversified family conglomerates, Atlas Hospitality Group benefits from deep local market knowledge and strong institutional relationships within the Moroccan real estate and tourism ecosystem.",
  'Zalagh Hotels Group': "Zalagh Hotels Group is a Moroccan hospitality company operating a portfolio of upscale hotels primarily in the imperial cities of Fes and Meknes, with a flagship property in Marrakech. The group's flagship Menzeh Zalagh City Center in Fes has been a landmark address in the city since 1988, serving as one of the premier hotels for business and leisure travelers visiting Morocco's cultural capital. With properties including the Zalagh Kasbah Hotel and Spa in Marrakech and the Zalagh Parc Palace in Meknes, the group has built a consistent upscale positioning across Morocco's most historically significant cities. Zalagh Hotels represents an important example of Moroccan-owned hospitality brands building lasting market presence in destinations where cultural authenticity and local expertise are key differentiators.",
  'Mia Hotels': "Mia Hotels is a Moroccan lifestyle hospitality brand offering a portfolio of urban and resort properties across the kingdom's key destinations including Agadir, Marrakech, Tanger, Fes, Dakhla, and El Jadida. Founded with a focus on delivering contemporary design and modern amenities at accessible price points, Mia Hotels targets the growing segment of domestic and regional travelers seeking quality midscale and upscale accommodation in Morocco's most dynamic cities and resort destinations. The brand's rapid expansion since 2023 across six properties reflects the growing demand for consistent, design-led hospitality from Morocco's emerging middle class and regional business travelers. Mia Hotels represents a new generation of Moroccan hospitality brands built on local market insight and a clear understanding of the modern Moroccan traveler's expectations.",
  'Zephyr': "Zephyr is a Moroccan hospitality and residential brand developed under the patronage of the Fondation Mohammed VI for Environmental Protection, operating a portfolio of eco-conscious resort and aparthotel properties in Morocco's most scenic natural destinations. The brand combines hotel rooms with residential apartment units, targeting both short-stay leisure guests and medium-term residents seeking premium amenities in resort settings. With properties in Agadir, Marrakech, Ifrane, and El Jadida, Zephyr has established a distinctive presence in Morocco's most sought-after natural and leisure environments. The brand's alignment with environmental values and its foundation sponsorship give it a unique institutional positioning that differentiates it from purely commercial hotel brands in the Moroccan market.",
  'Story Hospitality': "Story Hospitality is a boutique luxury hospitality brand developed by Imkan, the Abu Dhabi-based real estate developer and subsidiary of Abu Dhabi Capital Group, specializing in design-led urban hotels in culturally significant destinations. In Morocco, Story operates two properties in Rabat including the intimate Story Rabat and the larger Story Carousel Rabat, both positioned in the luxury segment and reflecting Imkan's commitment to creating hotels that are deeply rooted in the architectural and cultural heritage of their host cities. The brand's presence in Rabat signals growing Gulf institutional interest in Morocco's capital as a luxury hospitality destination, complementing the wave of international brand openings that have transformed Rabat's hotel landscape since 2020. Story Hospitality represents a new category of ownership-driven luxury brands entering Morocco, bringing with them Gulf capital, design ambition, and a long-term perspective on the kingdom's tourism potential.",
  'Farah Hotels': "Farah Hotels is a Moroccan hospitality brand with a legacy dating back to the 1970s, operating a small portfolio of upscale and midscale properties in Tanger and Ifrane. The brand's flagship Hotel Farah Tanger has been one of the city's established hotel addresses since 2010, serving both business and leisure travelers in Morocco's northern gateway city. The Farah Inn Ifrane, a midscale property in the mountain resort town of Ifrane, caters to domestic leisure travelers and families visiting the Middle Atlas region. As one of Morocco's older independent hotel brands, Farah Hotels represents the generation of locally owned hospitality businesses that laid the foundations of Morocco's modern hotel sector.",
  'TUI Hotels & Resorts': "TUI Hotels & Resorts is the proprietary hotel brand division of TUI Group, Europe's largest travel and tourism company, operating resort properties under brands including Robinson Club, TUI Blue, and TUI Suneo across popular leisure destinations. In Morocco, TUI operates two properties targeting distinct market segments: the Robinson Club Taghazout Bay, a premium club resort in the Taghazout surf destination, and the TUI Suneo Kenzi Agadir, a longstanding all-inclusive beach resort in Agadir that has served European package travelers since 1989. TUI's dual presence in both the premium club resort and mass-market all-inclusive segments reflects the group's strategy of capturing multiple price points within its vertically integrated tour operator and hotel business model. Morocco's strong connectivity with European source markets and its established package tourism infrastructure make it a natural and enduring market for TUI's resort brands.",
  'Aman Resorts': "Aman Resorts is one of the world's most exclusive ultra-luxury hospitality brands, founded in 1988 and operating a carefully curated portfolio of properties in extraordinary natural and cultural settings across Asia, Europe, the Americas, and the Middle East. In Morocco, Aman's single property is the iconic Amanjena in Marrakech, one of the brand's earliest African outposts and a defining presence in Morocco's ultra-luxury segment since its opening. Amanjena's rose-pink pavilions and basins set within a palm grove near the Royal Golf Club of Marrakech have made it one of the most recognizable and aspirational hotel addresses in the country. Aman's deliberate scarcity strategy and uncompromising service standards make its Morocco presence a significant marker of the country's maturity as an ultra-luxury destination.",
  'Mandarin Oriental Hotel Group': "Mandarin Oriental Hotel Group is a Hong Kong-based luxury hospitality company operating over 40 hotels across 25 countries, consistently ranked among the world's finest hotel groups. In Morocco, Mandarin Oriental operates a single luxury property in Marrakech, positioned at the very top of the city's hotel market with its signature spa offering, landscaped gardens, and the brand's hallmark blend of Asian-influenced service philosophy with local cultural sensibility. The property's presence in Marrakech reflects the brand's selective approach to market entry, choosing only destinations where it can command a leading luxury position. Mandarin Oriental Marrakech serves as a testament to the city's ability to attract the world's most discerning hotel brands and the most sophisticated international leisure travelers.",
  'Oberoi Hotels & Resorts': "Oberoi Hotels & Resorts is an Indian luxury hospitality company founded in 1934 and one of Asia's most celebrated hotel groups, operating properties across India, Egypt, Indonesia, Mauritius, and Morocco. The Oberoi Marrakech, opened in 2023 with 84 rooms and villas, represents the brand's sole African outpost outside Egypt and one of the most anticipated ultra-luxury openings in Marrakech in recent years. The property brings Oberoi's signature combination of meticulous service, elegant design, and exceptional culinary experiences to Morocco's most competitive luxury market, immediately establishing itself among the city's finest addresses. Oberoi's entry into Morocco adds an important Asian luxury perspective to a hotel market historically dominated by European and American brands, and signals Marrakech's continued ability to attract first-time entries from globally prestigious operators.",
  'Nobu Hospitality': "Nobu Hospitality is a global luxury lifestyle brand co-founded by chef Nobu Matsuhisa and actor Robert De Niro, operating a portfolio of hotels and restaurants that combine Japanese-influenced culinary philosophy with contemporary luxury design across major global cities and resort destinations. In Morocco, Nobu operates its first African property with the Nobu Hotel Marrakech, opened in 2024 and positioned in the luxury segment as a design-forward lifestyle hotel anchored by the brand's celebrated restaurant concept. The hotel's opening in Marrakech reflects the growing appetite among lifestyle-focused luxury travelers for branded experiences that combine world-class dining with premium accommodation in culturally rich destinations. Nobu Hotel Marrakech adds a distinct lifestyle and culinary dimension to the city's luxury hotel offer that differentiates it from the more traditional luxury palace hotels that have long defined Marrakech's upper segment.",
  'Pestana Hotel Group': "Pestana Hotel Group is a Portuguese hospitality company founded in 1972 and the largest hotel group in Portugal, operating over 100 properties across 16 countries with a particular strength in Portuguese-speaking markets and leisure destinations. In Morocco, Pestana operates two properties including the Pestana CR7 Marrakech, a lifestyle hotel developed in partnership with global football icon Cristiano Ronaldo and opened in 2022 with 174 rooms, and the Pestana Tanger serving the upper upscale segment in Morocco's northern gateway city. The CR7 brand partnership reflects Pestana's innovative approach to lifestyle hospitality and the growing crossover between sports celebrity and luxury hotel development, positioning Marrakech as one of the brand's most high-profile global addresses. Pestana's Morocco portfolio demonstrates the group's ambition to combine commercial lifestyle concepts with traditional upscale hospitality across two of Morocco's most strategically important destinations.",
  'Relais & Châteaux': "Relais & Châteaux is a French association of independently owned luxury hotels and restaurants founded in 1954, uniting over 580 properties across 60 countries under a shared commitment to exceptional gastronomy, architectural heritage, and personalised hospitality. In Morocco, Relais & Châteaux is represented by two distinctive properties: the Riad Fès in the medina of Fes and La Villa des Orangers in Marrakech, both of which exemplify the association's core values of intimacy, authenticity, and deep rootedness in their cultural and architectural context. The presence of Relais & Châteaux properties in Morocco reflects the country's recognition within the global community of connoisseur travelers who seek singular experiences over standardised luxury. Both Moroccan members of the collection are among the most celebrated small luxury hotels in North Africa and represent a pinnacle of the riad and boutique hotel tradition.",
  'Wyndham Hotels & Resorts': "Wyndham Hotels & Resorts is the world's largest hotel franchising company by number of properties, operating over 9,000 hotels across 95 countries through a portfolio of 24 brands spanning economy to upper upscale segments. In Morocco, Wyndham's presence is represented through the Ramada Encore by Wyndham brand in Tanger, targeting the upper midscale and upscale business and leisure traveler segment in one of Morocco's fastest-growing hotel markets. The group's selective approach to Morocco reflects a broader strategy of using franchise partnerships to establish a foothold in emerging markets before expanding through additional brand tiers. Wyndham's global loyalty program and distribution network provide its Morocco property with connectivity to a vast base of international travelers that would otherwise be difficult to reach through independent channels.",
  'Louvre Hotels Group': "Louvre Hotels Group is a French hospitality company and one of Europe's largest hotel groups, operating over 1,500 hotels across 54 countries through brands including Golden Tulip, Tulip Inn, and Royal Tulip. In Morocco, Louvre Hotels Group is represented by the Royal Tulip City Center Tanger, an upper upscale property in the heart of Morocco's northern commercial hub. The Royal Tulip brand targets the upper upscale business and leisure segment with a focus on full-service amenities and prime city center locations, making Tanger a natural fit given the city's growing importance as a regional business and logistics hub. Louvre Hotels Group's presence in Morocco reflects the country's attractiveness to mid-to-large European hotel groups seeking to establish footholds in North Africa's most accessible and stable tourism market.",
};

function getBrandLogoUrl(brandGroup) {
  const domain = BRAND_DOMAINS[brandGroup];
  if (!domain) return null;
  return `https://cdn.brandfetch.io/domain/${domain}?c=1idptYpdMe9b8BdTIPC`;
}

function getBrandLogoImg(brandGroup, size = 24) {
  console.log('getBrandLogoImg called with:', brandGroup);
  const local = LOCAL_BRAND_LOGOS[brandGroup];
  if (local) {
    const custom = BRAND_CUSTOM_LOGOS[brandGroup];
    const fallback = custom
      ? `this.outerHTML=\`<span style='display:inline-flex;align-items:center;justify-content:center;width:${size}px;height:${size}px;background:${custom.bg};color:${custom.color};border-radius:4px;font-family:Syne,sans-serif;font-weight:700;font-size:${Math.round(size * 0.55)}px;flex-shrink:0;vertical-align:middle;margin-right:6px;'>${custom.letter}</span>\``
      : `this.style.display='none'`;
    return `<img src="${local}" alt="${brandGroup}" style="width:${size}px;height:${size}px;object-fit:contain;vertical-align:middle;border-radius:3px;background:white;padding:2px;margin-right:6px;" onerror="${fallback}">`;
  }
  const custom = BRAND_CUSTOM_LOGOS[brandGroup];
  if (custom) {
    return `<span style="display:inline-flex;align-items:center;justify-content:center;width:${size}px;height:${size}px;background:${custom.bg};color:${custom.color};border-radius:4px;font-family:'Syne',sans-serif;font-weight:700;font-size:${Math.round(size * 0.55)}px;letter-spacing:0;flex-shrink:0;vertical-align:middle;margin-right:6px;">${custom.letter}</span>`;
  }
  const domain = BRAND_DOMAINS[brandGroup];
  if (!domain) return '';
  return `<img src="https://cdn.brandfetch.io/domain/${domain}?c=1idptYpdMe9b8BdTIPC" alt="${brandGroup}" style="width:${size}px;height:${size}px;object-fit:contain;vertical-align:middle;border-radius:3px;background:white;padding:2px;margin-right:6px;" onerror="this.style.display='none'">`;
}

const SEG_COLORS = {
  'Ultra Luxury': '#B87860',
  'Luxury':       '#A06848',
  'Upper Upscale':'#886050',
  'Upscale':      '#705040',
  'Midscale':     '#584038',
  'Economy':      '#403028',
};

const CITY_COORDS = {
  'Casablanca':  [33.573, -7.589],
  'Marrakech':   [31.629, -7.981],
  'Agadir':      [30.427, -9.598],
  'Tanger':      [35.769, -5.800],
  'Tamuda Bay / Tétouan':    [35.630, -5.380],
  'Rabat / Salé / Témara':  [34.020, -6.841],
  'Fes':         [34.037, -4.998],
};

const MOROCCO_CENTER  = [-5.5, 31.5];  // [lng, lat] — Mapbox order
const MOROCCO_ZOOM    = 5.5;
const CITY_ZOOM       = 10;
const GMAP_STYLE_DARK = [
  {"elementType":"geometry","stylers":[{"color":"#141414"}]},
  {"elementType":"labels.text.fill","stylers":[{"color":"#888888"}]},
  {"elementType":"labels.text.stroke","stylers":[{"color":"#0A0A0A"}]},
  {"featureType":"administrative","elementType":"geometry","stylers":[{"color":"#242424"}]},
  {"featureType":"administrative.country","elementType":"geometry.stroke","stylers":[{"color":"#444444"}]},
  {"featureType":"administrative.province","elementType":"geometry.stroke","stylers":[{"color":"#242424"}]},
  {"featureType":"road","elementType":"geometry","stylers":[{"color":"#1C1C1C"}]},
  {"featureType":"road.highway","elementType":"geometry","stylers":[{"color":"#242424"}]},
  {"featureType":"water","elementType":"geometry","stylers":[{"color":"#0A0A0A"}]},
  {"featureType":"poi","stylers":[{"visibility":"off"}]},
  {"featureType":"transit","stylers":[{"visibility":"off"}]},
];
const GMAP_STYLE_LIGHT = [
  {"elementType":"geometry","stylers":[{"color":"#F5F5F5"}]},
  {"elementType":"labels.text.fill","stylers":[{"color":"#616161"}]},
  {"elementType":"labels.text.stroke","stylers":[{"color":"#F5F5F5"}]},
  {"featureType":"administrative.country","elementType":"geometry.stroke","stylers":[{"color":"#CCCCCC"}]},
  {"featureType":"road","elementType":"geometry","stylers":[{"color":"#FFFFFF"}]},
  {"featureType":"road.highway","elementType":"geometry","stylers":[{"color":"#E0E0E0"}]},
  {"featureType":"water","elementType":"geometry","stylers":[{"color":"#C9D8E8"}]},
  {"featureType":"poi","stylers":[{"visibility":"off"}]},
  {"featureType":"transit","stylers":[{"visibility":"off"}]},
];


const KPI_DELTAS = {
  'kpi-keys':   { text: '+6.2% YoY',    up: true },
  'kpi-occ':    { text: '+3.1 pts YoY', up: true },
  'kpi-adr':    { text: '+8.4% YoY',    up: true },
  'kpi-revpar': { text: '+10.8% YoY',   up: true },
};

Chart.register(ChartDataLabels);

// Global: no grid lines, tick marks or axis borders on any chart
Chart.defaults.scale.grid.display   = false;
Chart.defaults.scale.grid.drawTicks = false;
Chart.defaults.scale.border.display = false;
Chart.defaults.font.family = "'Helvetica Neue', Helvetica, Arial, sans-serif";

// ─── State & cache ────────────────────────────────────────────────

const state = {
  city:    'all',
  mapSeg:  'all',
};

let apiData  = null;   // /api/data response
let hotels   = null;   // /api/hotels response (flat, merged)
let revChart = null;
let occChart = null;
let googleMap          = null;
let googlePipelineMap  = null;
let googleMapsApiReady = false;
let hotelMarkers       = [];   // [{marker, hotel}]
let pipelineMarkers    = [];   // [{marker, project}]
let activeInfoWindow   = null;
let brandChart      = null;
let brandHotelsData = [];
const brandState    = { col: 'name', dir: 1 };
let activeBrandCity = null;
const BRAND_STR_COLS = new Set(['name', 'city', 'category', 'owner']);
let tourismInited   = false;
let pipelineInited  = false;
let pipelineData    = null;
const pipelineState = { status: 'all', city: 'all', category: 'all' };
const pipelineSort  = { col: 'expected_opening', dir: 1 };
const PIPE_STR_COLS = new Set(['name', 'city', 'category', 'brand', 'status']);

let hotelDetailPrevScreen = 'hotels';
let hotelCityChart        = null;

let brandsData   = null;
let brandsInited = false;
let brandDetailPrevScreen = 'dashboard';
const brandsFilter   = { sort: 'total_keys', search: '', segment: 'all' };
const brandsCompSort = { col: 'total_keys', dir: -1 };
const BRANDS_STR_COLS = new Set(['brand_group']);
const BRAND_PALETTE   = [
  '#B87860','#A06848','#886050','#705040','#584038',
  '#3E2E28','#6A8A6A','#4A6E8A','#7A6A8A','#8A6A4A',
];
const BRANDS_COMP_STR = new Set(['brand_group']);

// ─── Theme ────────────────────────────────────────────────────────

const ICON_MOON = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>`;
const ICON_SUN  = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>`;

function applyTheme(mode) {
  const icon = document.getElementById('theme-icon');
  if (mode === 'light') {
    document.body.classList.add('light');
    icon.innerHTML = ICON_SUN;
  } else {
    document.body.classList.remove('light');
    icon.innerHTML = ICON_MOON;
  }
  swapMapTheme(mode);
}

document.getElementById('theme-toggle').addEventListener('click', () => {
  const next = document.body.classList.contains('light') ? 'dark' : 'light';
  localStorage.setItem('kodo-theme', next);
  applyTheme(next);
  redrawChartsForTheme();
});

applyTheme(localStorage.getItem('kodo-theme') || 'light');

// ─── Formatters ───────────────────────────────────────────────────

const fmt = {
  pct: v  => (v * 100).toFixed(1) + '%',
  num: v  => Math.round(v).toLocaleString('en'),
  mad: v  => Math.round(v).toLocaleString('en'),
  esc: s  => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'),
};

// ─── Aggregation ──────────────────────────────────────────────────

function cityAggs(hotelList) {
  const map = new Map();
  hotelList.forEach(h => {
    if (!map.has(h.city)) map.set(h.city, []);
    map.get(h.city).push(h);
  });
  return [...map.entries()].map(([city, hs]) => {
    const tk = hs.reduce((s, h) => s + h.keys, 0);
    const ok = hs.reduce((s, h) => s + h.keys * h.occupancy, 0);
    return {
      city,
      hotel_count: hs.length,
      total_keys:  tk,
      occupancy:   ok / tk,
      adr_mad:     hs.reduce((s, h) => s + h.adr_mad * h.keys * h.occupancy, 0) / ok,
      revpar_mad:  hs.reduce((s, h) => s + h.revpar_mad * h.keys, 0) / tk,
      gop_margin:  hs.reduce((s, h) => s + h.gop_margin * h.keys, 0) / tk,
    };
  });
}

function brandAggs(hotelList) {
  const map = new Map();
  hotelList.forEach(h => {
    if (!map.has(h.brand_group)) map.set(h.brand_group, []);
    map.get(h.brand_group).push(h);
  });
  return [...map.entries()].map(([bg, hs]) => {
    const tk = hs.reduce((s, h) => s + h.keys, 0);
    const ok = hs.reduce((s, h) => s + h.keys * h.occupancy, 0);
    return {
      brand_group:  bg,
      hotel_count:  hs.length,
      total_keys:   tk,
      occupancy:    ok / tk,
      adr_mad:      hs.reduce((s, h) => s + h.adr_mad * h.keys * h.occupancy, 0) / ok,
      revpar_mad:   hs.reduce((s, h) => s + h.revpar_mad * h.keys, 0) / tk,
      gop_margin:   hs.reduce((s, h) => s + h.gop_margin * h.keys, 0) / tk,
    };
  }).sort((a, b) => b.total_keys - a.total_keys);
}

function nationalKPIs(hotelList) {
  const tk = hotelList.reduce((s, h) => s + h.keys, 0);
  const ok = hotelList.reduce((s, h) => s + h.keys * h.occupancy, 0);
  return {
    total_hotels: hotelList.length,
    total_keys:   tk,
    occupancy:    ok / tk,
    adr_mad:      hotelList.reduce((s, h) => s + h.adr_mad * h.keys * h.occupancy, 0) / ok,
    revpar_mad:   hotelList.reduce((s, h) => s + h.revpar_mad * h.keys, 0) / tk,
    gop_margin:   hotelList.reduce((s, h) => s + h.gop_margin * h.keys, 0) / tk,
  };
}

function filteredByCity() {
  if (state.city === 'all') return hotels;
  return hotels.filter(h => h.city === state.city);
}

// ─── KPIs ─────────────────────────────────────────────────────────

function renderKPIs() {
  const kpis = nationalKPIs(filteredByCity());

  const set = (id, val, meta) => {
    const el = document.getElementById(id);
    el.querySelector('.kpi-value').textContent = val;
    if (meta !== undefined) {
      const m = document.getElementById(id + '-meta');
      if (m) m.textContent = meta;
    }
    const d = KPI_DELTAS[id];
    if (d) {
      const deltaEl = document.getElementById(id + '-delta');
      if (deltaEl) {
        deltaEl.textContent = d.text;
        deltaEl.className = 'kpi-delta ' + (d.up ? 'up' : 'down');
      }
    }
    el.classList.remove('loading');
  };

  const hotelLabel = kpis.total_hotels + ' hotel' + (kpis.total_hotels !== 1 ? 's' : '');
  set('kpi-keys',   fmt.num(kpis.total_keys), hotelLabel);
  set('kpi-occ',    fmt.pct(kpis.occupancy),  '');
  set('kpi-adr',    fmt.mad(kpis.adr_mad));
  set('kpi-revpar', fmt.mad(kpis.revpar_mad));

  const sub = document.getElementById('dashboard-sub');
  sub.textContent = state.city === 'all'
    ? 'Morocco branded hotel market · Kōdō Estimates'
    : state.city + ' · Kōdō Estimates · ' + hotelLabel;
}

// ─── Charts ───────────────────────────────────────────────────────

function getChartColors() {
  const dark = !document.body.classList.contains('light');
  return {
    barColor:   dark ? '#B87860' : '#A06848',
    hoverColor: dark ? '#C98870' : '#B07858',
    fillColor:  dark ? 'rgba(184,120,96,0.08)' : 'rgba(160,104,72,0.08)',
    gridColor:  'transparent',
    tick:       dark ? '#888888' : '#888888',
    label:      dark ? '#888888' : '#888888',
    catLabel:   dark ? '#AAAAAA' : '#555555',
    tooltipBg:  dark ? '#141414' : '#FFFFFF',
    tooltipBdr: dark ? '#242424' : '#E4E4E4',
    tooltipTtl: dark ? '#F0F0EE' : '#1A1A1A',
    tooltipBdy: dark ? '#888888' : '#888888',
  };
}

function chartConfig(labels, values, tooltipSuffix, bgColors, labelFmt) {
  const cc = getChartColors();
  return {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: bgColors,
        hoverBackgroundColor: cc.hoverColor,
        borderRadius: 4,
        borderSkipped: false,
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 350 },
      layout: { padding: { right: 72 } },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: cc.tooltipBg,
          borderColor: cc.tooltipBdr,
          borderWidth: 1,
          titleColor: cc.tooltipTtl,
          bodyColor: cc.tooltipBdy,
          padding: { top: 8, bottom: 8, left: 12, right: 12 },
          callbacks: {
            label: ctx => '  ' + Math.round(ctx.raw).toLocaleString('en') + tooltipSuffix,
          }
        },
        datalabels: {
          anchor: 'end',
          align: 'right',
          clip: false,
          color: cc.label,
          font: { size: 11, weight: '600' },
          padding: { left: 5 },
          formatter: labelFmt,
        },
      },
      scales: {
        x: {
          min: 0,
          ticks: { color: cc.tick, font: { size: 11 } }
        },
        y: {
          ticks: { color: cc.catLabel, font: { size: 12, weight: '500' } }
        }
      }
    }
  };
}

function barColors(labels) {
  const color = getChartColors().barColor;
  return labels.map(() => color);
}

function renderCharts() {
  const allCityData = cityAggs(hotels);

  // Set chart container heights based on city count (30px per bar + padding)
  const chartH = Math.max(400, allCityData.length * 30 + 60);
  document.getElementById('chart-revpar').closest('.chart-wrap').style.height = chartH + 'px';
  document.getElementById('chart-occ').closest('.chart-wrap').style.height = chartH + 'px';

  // RevPAR chart — sorted high→low
  const revSorted = [...allCityData].sort((a, b) => b.revpar_mad - a.revpar_mad);
  const revLabels = revSorted.map(c => c.city);
  const revVals   = revSorted.map(c => c.revpar_mad);

  const revLabelFmt = v => Math.round(v).toLocaleString('en');
  if (revChart) {
    revChart.data.labels = revLabels;
    revChart.data.datasets[0].data = revVals;
    revChart.data.datasets[0].backgroundColor = barColors(revLabels);
    revChart.update();
  } else {
    revChart = new Chart(
      document.getElementById('chart-revpar'),
      chartConfig(revLabels, revVals, ' MAD', barColors(revLabels), revLabelFmt)
    );
  }

  // Occupancy chart — sorted high→low
  const occSorted  = [...allCityData].sort((a, b) => b.occupancy - a.occupancy);
  const occLabels  = occSorted.map(c => c.city);
  const occVals    = occSorted.map(c => parseFloat((c.occupancy * 100).toFixed(1)));
  const occLabelFmt = v => v.toFixed(1) + '%';

  if (occChart) {
    occChart.data.labels = occLabels;
    occChart.data.datasets[0].data = occVals;
    occChart.data.datasets[0].backgroundColor = barColors(occLabels);
    occChart.update();
  } else {
    const cfg = chartConfig(occLabels, occVals, '%', barColors(occLabels), occLabelFmt);
    cfg.options.plugins.tooltip.callbacks.label = ctx => '  ' + ctx.raw.toFixed(1) + '%';
    occChart = new Chart(document.getElementById('chart-occ'), cfg);
  }
}

// ─── Brand table ──────────────────────────────────────────────────

function renderBrandTable() {
  const rows = brandAggs(filteredByCity());
  const tbody = document.querySelector('#brand-table tbody');

  tbody.innerHTML = rows.map((r, i) => `
    <tr>
      <td class="rank-cell">${i + 1}</td>
      <td><button class="brand-link" data-brand="${fmt.esc(r.brand_group)}" onclick="showBrandDetail(this.dataset.brand)">${getBrandLogoImg(r.brand_group, 20)} ${fmt.esc(r.brand_group)}</button></td>
      <td>${r.hotel_count}</td>
      <td>${fmt.num(r.total_keys)}</td>
      <td>${fmt.pct(r.occupancy)}</td>
      <td>${fmt.mad(r.adr_mad)}</td>
      <td>${fmt.mad(r.revpar_mad)}</td>
    </tr>
  `).join('');

  const sub = document.getElementById('brand-table-sub');
  const dest = state.city === 'all' ? 'All destinations' : state.city;
  sub.textContent = `${dest} · ${rows.length} group${rows.length !== 1 ? 's' : ''}`;
}

// ─── Brands screen ────────────────────────────────────────────────

async function initBrands() {
  if (!brandsInited) {
    try {
      brandsData   = await fetch('/api/brands').then(r => r.json());
      brandsInited = true;
    } catch (e) {
      document.getElementById('brands-cards-grid').innerHTML =
        '<p style="color:var(--text-muted);font-size:13px;padding:16px 0">Failed to load brand data.</p>';
      return;
    }
  }
  renderBrandsKPIs();
  renderBrandsCards();
  renderBrandsMarketShare();
  renderBrandsCompTable();
  renderBrandsInsights();
}

function filteredBrands() {
  let data = [...brandsData];
  if (brandsFilter.segment !== 'all') {
    data = data.filter(b => b.segments.includes(brandsFilter.segment));
  }
  if (brandsFilter.search.trim()) {
    const q = brandsFilter.search.trim().toLowerCase();
    data = data.filter(b => b.brand_group.toLowerCase().includes(q));
  }
  data.sort((a, b) => b[brandsFilter.sort] - a[brandsFilter.sort]);
  return data;
}

function renderBrandsKPIs() {
  const branded = brandsData.filter(b => b.brand_group !== 'Independent Hotels');
  const allKeys = brandsData.reduce((s, b) => s + b.total_keys, 0);
  const champion = [...brandsData].sort((a, b) => b.weighted_revpar - a.weighted_revpar)[0];
  const largest  = [...brandsData].sort((a, b) => b.total_keys - a.total_keys)[0];

  document.querySelector('#brnkpi-groups .kpi-value').textContent  = brandsData.length;
  document.querySelector('#brnkpi-keys .kpi-value').textContent    = allKeys.toLocaleString('en');
  document.querySelector('#brnkpi-champion .kpi-value').textContent = champion ? champion.brand_group : '—';
  document.querySelector('#brnkpi-largest .kpi-value').textContent  = largest  ? largest.brand_group  : '—';
}

function brandLogoOrInitials(bg, size) {
  const url = getBrandLogoUrl(bg);
  if (url) return getBrandLogoImg(bg, size);
  const initials = bg.replace('Hotels', '').replace('Hotel', '').replace('Resorts', '').replace('International', '')
    .trim().split(/\s+/).slice(0, 2).map(w => w[0]).join('').toUpperCase();
  const bg2 = BRAND_PALETTE[Math.abs(bg.split('').reduce((s, c) => s + c.charCodeAt(0), 0)) % BRAND_PALETTE.length];
  return `<div class="brn-initials" style="width:${size}px;height:${size}px;background:${bg2}">${initials}</div>`;
}

function renderBrandsCards() {
  const data = filteredBrands();
  const grid = document.getElementById('brands-cards-grid');
  if (!data.length) {
    grid.innerHTML = '<p style="color:var(--text-muted);font-size:13px;padding:16px 0">No brands match the selected filters.</p>';
    return;
  }
  grid.innerHTML = data.map(b => {
    const cityList  = b.cities.slice(0, 3).map(fmt.esc).join(' · ');
    const cityMore  = b.cities.length > 3 ? ` <span class="brn-more">+${b.cities.length - 3}</span>` : '';
    const segPills  = b.segments.map(s => `<span class="brn-seg-pill">${fmt.esc(s)}</span>`).join('');
    const mktBar    = Math.min(b.market_share_keys_pct * 4, 100);
    const pipeRow   = b.pipeline_projects > 0
      ? `<div class="brn-card-pipeline">Pipeline: ${b.pipeline_projects} project${b.pipeline_projects !== 1 ? 's' : ''} · ${b.pipeline_keys.toLocaleString('en')} keys →</div>`
      : '';
    const _desc     = BRAND_DESCRIPTIONS[b.brand_group] || '';
    const descRow   = _desc
      ? `<p class="brand-card-teaser">${fmt.esc(_desc.split('.')[0] + '.')}</p>`
      : '';
    const esc = fmt.esc(b.brand_group).replace(/'/g, '&#39;');

    return `<div class="brn-card" data-brand-group="${esc}">
      <div class="brn-card-header">
        <div class="brn-card-logo-wrap">${brandLogoOrInitials(b.brand_group, 40)}</div>
        <div class="brn-card-header-info">
          <div class="brn-card-name">${fmt.esc(b.brand_group)}</div>
          <div class="brn-card-sub">${b.hotels} hotel${b.hotels !== 1 ? 's' : ''} · ${b.total_keys.toLocaleString('en')} keys</div>
        </div>
      </div>
      ${descRow}
      <div class="brn-card-kpis">
        <div class="brn-kpi"><div class="brn-kpi-lbl">OCC</div><div class="brn-kpi-val">${fmt.pct(b.avg_occupancy)}</div></div>
        <div class="brn-kpi"><div class="brn-kpi-lbl">ADR</div><div class="brn-kpi-val">${fmt.mad(b.avg_adr)}</div></div>
        <div class="brn-kpi"><div class="brn-kpi-lbl">RevPAR</div><div class="brn-kpi-val">${fmt.mad(b.weighted_revpar)}</div></div>
      </div>
      <div class="brn-card-meta">
        <div class="brn-card-cities">${cityList}${cityMore}</div>
        <div class="brn-card-segs">${segPills}</div>
      </div>
      <div class="brn-card-share">
        <span class="brn-share-txt">Mkt share: ${b.market_share_keys_pct.toFixed(1)}% of keys</span>
        <div class="brn-share-mini"><div class="brn-share-mini-fill" style="width:${mktBar}%"></div></div>
        ${pipeRow}
      </div>
      <button class="brn-card-link" data-brand-group="${esc}">View all properties →</button>
    </div>`;
  }).join('');
}

function renderBrandsMarketShare() {
  const sorted = [...brandsData].sort((a, b) => b.total_keys - a.total_keys);
  const total  = sorted.reduce((s, b) => s + b.total_keys, 0);
  const top8   = sorted.slice(0, 8);
  const others = sorted.slice(8);
  const otherKeys = others.reduce((s, b) => s + b.total_keys, 0);

  const segs = top8.map((b, i) => ({
    name:  b.brand_group,
    pct:   b.total_keys / total * 100,
    color: BRAND_PALETTE[i] || '#888888',
  }));
  if (otherKeys > 0) segs.push({ name: 'Other', pct: otherKeys / total * 100, color: '#444444' });

  const barHtml = segs.map(s =>
    `<div class="brn-mkt-seg" style="width:${s.pct.toFixed(2)}%;background:${s.color}" title="${s.name}: ${s.pct.toFixed(1)}%"></div>`
  ).join('');

  const legendHtml = segs.map(s =>
    `<div class="brn-mkt-legend-item">
      <span class="brn-mkt-dot" style="background:${s.color}"></span>
      <span class="brn-mkt-label">${fmt.esc(s.name)}</span>
      <span class="brn-mkt-pct">${s.pct.toFixed(1)}%</span>
    </div>`
  ).join('');

  document.getElementById('brands-market-share-wrap').innerHTML =
    `<div class="brn-mkt-bar">${barHtml}</div>
     <div class="brn-mkt-legend">${legendHtml}</div>`;
}

function renderBrandsCompTable() {
  const { col, dir } = brandsCompSort;
  const sorted = [...brandsData].sort((a, b) => {
    if (BRANDS_COMP_STR.has(col)) return dir * String(a[col]).localeCompare(String(b[col]));
    return dir * (a[col] - b[col]);
  });

  document.querySelectorAll('#brands-comp-table .sortable-col').forEach(th => {
    th.classList.remove('sort-asc', 'sort-desc');
    const icon = th.querySelector('.sort-icon');
    if (th.dataset.bccol === col) {
      th.classList.add(dir === 1 ? 'sort-asc' : 'sort-desc');
      if (icon) icon.textContent = dir === 1 ? '↑' : '↓';
    } else {
      if (icon) icon.textContent = '↕';
    }
  });

  document.getElementById('brands-comp-tbody').innerHTML = sorted.map((b, i) => {
    const rank      = i + 1;
    const topClass  = rank <= 3 ? ' brn-top3' : '';
    const rankStyle = rank <= 3 ? `style="color:var(--accent);font-weight:700"` : '';
    return `<tr class="brand-hotel-row${topClass}" data-brand-group="${fmt.esc(b.brand_group).replace(/'/g,'&#39;')}">
      <td class="rank-cell" ${rankStyle}>${rank}</td>
      <td>
        <button class="brand-link" data-brand-group="${fmt.esc(b.brand_group).replace(/'/g,'&#39;')}" style="display:flex;align-items:center;gap:6px">
          ${getBrandLogoImg(b.brand_group, 20)} ${fmt.esc(b.brand_group)}
        </button>
      </td>
      <td>${b.hotels}</td>
      <td>${b.total_keys.toLocaleString('en')}</td>
      <td>${b.market_share_keys_pct.toFixed(1)}%</td>
      <td>${fmt.pct(b.avg_occupancy)}</td>
      <td>${fmt.mad(b.avg_adr)}</td>
      <td>${fmt.mad(b.weighted_revpar)}</td>
      <td>${b.pipeline_keys > 0 ? b.pipeline_keys.toLocaleString('en') : '—'}</td>
    </tr>`;
  }).join('');
}

function renderBrandsInsights() {
  const byKeys   = [...brandsData].sort((a, b) => b.total_keys   - a.total_keys)[0];
  const byRevpar = [...brandsData].sort((a, b) => b.weighted_revpar - a.weighted_revpar)[0];
  const byPipe   = [...brandsData].filter(b => b.pipeline_projects > 0)
                                   .sort((a, b) => b.pipeline_keys - a.pipeline_keys)[0];
  const totalKeys = brandsData.reduce((s, b) => s + b.total_keys, 0);

  if (byKeys) {
    document.getElementById('brni-leader-val').textContent  = byKeys.brand_group;
    document.getElementById('brni-leader-desc').textContent =
      `${byKeys.market_share_keys_pct.toFixed(1)}% of all Morocco hotel keys`;
  }
  if (byRevpar) {
    document.getElementById('brni-revpar-val').textContent  = byRevpar.brand_group;
    document.getElementById('brni-revpar-desc').textContent =
      `MAD ${fmt.mad(byRevpar.weighted_revpar)} weighted RevPAR`;
  }
  if (byPipe) {
    document.getElementById('brni-pipeline-val').textContent  = byPipe.brand_group;
    document.getElementById('brni-pipeline-desc').textContent =
      `${byPipe.pipeline_projects} projects · ${byPipe.pipeline_keys.toLocaleString('en')} keys in pipeline`;
  } else {
    document.getElementById('brni-pipeline-val').textContent  = '—';
    document.getElementById('brni-pipeline-desc').textContent = 'No pipeline data available';
  }
}

// ─── Brand detail ─────────────────────────────────────────────────

function showBrandDetail(brandGroup, prevScreen) {
  brandDetailPrevScreen = prevScreen || 'dashboard';
  const backBtn = document.getElementById('brand-back-btn');
  backBtn.textContent = brandDetailPrevScreen === 'brands' ? '← Back to Brands' : '← Back to Dashboard';

  brandHotelsData = hotels.filter(h => h.brand_group === brandGroup
    || (brandGroup === 'Independent Hotels' && (h.brand_group === 'Independent' || h.brand_group === 'Independent Luxury')));

  const tk    = brandHotelsData.reduce((s, h) => s + h.keys, 0);
  const ok    = brandHotelsData.reduce((s, h) => s + h.keys * h.occupancy, 0);
  const occ   = ok / tk;
  const adr   = brandHotelsData.reduce((s, h) => s + h.adr_mad * h.keys * h.occupancy, 0) / ok;
  const revpar= brandHotelsData.reduce((s, h) => s + h.revpar_mad * h.keys, 0) / tk;
  const cities      = [...new Set(brandHotelsData.map(h => h.city))].sort();
  const ownerValues = [...new Set(brandHotelsData.map(h => h.owner).filter(Boolean))];
  const distinctOwners = ownerValues.filter(o => o !== 'Undisclosed');

  // Header
  document.getElementById('brand-detail-name').innerHTML = getBrandLogoImg(brandGroup, 40) + ' ' + fmt.esc(brandGroup);
  document.getElementById('brand-meta-hotels').textContent = `${brandHotelsData.length} Hotel${brandHotelsData.length !== 1 ? 's' : ''}`;
  document.getElementById('brand-meta-keys').textContent   = `${fmt.num(tk)} Keys`;

  const ownerBadge = document.getElementById('brand-owner-badge');
  if (distinctOwners.length === 1) {
    ownerBadge.textContent = `· Owned by ${distinctOwners[0]}`;
    ownerBadge.style.display = '';
  } else {
    ownerBadge.style.display = 'none';
  }

  activeBrandCity = null;
  const visibleCities = cities.slice(0, 5);
  const hiddenCities  = cities.slice(5);
  const mkCityPill = c =>
    `<span class="brand-city-pill" data-city="${fmt.esc(c)}" onclick="filterBrandHotelsByCity('${fmt.esc(c).replace(/'/g, "\\'")}')">${fmt.esc(c)}</span>`;
  const hiddenHtml  = hiddenCities.length
    ? `<span class="brand-cities-hidden">${hiddenCities.map(mkCityPill).join('')}</span>`
    : '';
  const moreHtml    = hiddenCities.length
    ? `<span class="brand-cities-more" onclick="expandBrandCities(this)">+${hiddenCities.length} more</span>`
    : '';
  document.getElementById('brand-cities-row').innerHTML =
    `<span class="brand-cities-label">Present in</span>` +
    `<span class="brand-city-pill active" data-city="" onclick="filterBrandHotelsByCity(null)">All Cities</span>` +
    visibleCities.map(mkCityPill).join('') +
    hiddenHtml + moreHtml;

  // KPI cards
  const setKpi = (id, val) => {
    const el = document.getElementById(id);
    el.querySelector('.kpi-value').textContent = val;
  };
  setKpi('brand-bkpi-keys',   fmt.num(tk));
  setKpi('brand-bkpi-occ',    fmt.pct(occ));
  setKpi('brand-bkpi-adr',    fmt.mad(adr));
  setKpi('brand-bkpi-revpar', fmt.mad(revpar));

  // Switch to brand screen FIRST so the canvas has visible dimensions for Chart.js
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById('screen-brand').classList.add('active');
  setSidebar('brand');

  // About card
  const description = BRAND_DESCRIPTIONS[brandGroup] || '';
  const aboutSlot = document.getElementById('brand-about-slot');
  aboutSlot.innerHTML = description
    ? `<div class="brand-about-card">
        <div class="brand-about-title">About ${fmt.esc(brandGroup)}</div>
        <div class="brand-about-divider"></div>
        <p class="brand-about-body">${fmt.esc(description)}</p>
      </div>`
    : '';

  // City RevPAR chart
  const cityData = cityAggs(brandHotelsData).sort((a, b) => b.revpar_mad - a.revpar_mad);
  const chartH   = Math.max(240, cityData.length * 38 + 50);
  document.getElementById('brand-chart-wrap').style.height = chartH + 'px';

  const labels = cityData.map(c => c.city);
  const values = cityData.map(c => c.revpar_mad);
  const colors = labels.map(() => getChartColors().barColor);

  if (brandChart) {
    brandChart.data.labels                          = labels;
    brandChart.data.datasets[0].data               = values;
    brandChart.data.datasets[0].backgroundColor    = colors;
    brandChart.update();
  } else {
    brandChart = new Chart(
      document.getElementById('chart-brand-revpar'),
      chartConfig(labels, values, ' MAD', colors, v => Math.round(v).toLocaleString('en'))
    );
  }

  // Hotel table
  brandState.col = 'name';
  brandState.dir = 1;
  renderBrandHotelsTable();

}

function renderBrandHotelsTable() {
  const { col, dir } = brandState;
  const filtered = activeBrandCity
    ? brandHotelsData.filter(h => h.city === activeBrandCity)
    : brandHotelsData;
  const sorted = [...filtered].sort((a, b) => {
    const va = a[col], vb = b[col];
    if (BRAND_STR_COLS.has(col)) return dir * String(va).localeCompare(String(vb));
    return dir * (va - vb);
  });

  document.getElementById('brand-hotels-title').textContent =
    activeBrandCity
      ? `${sorted.length} hotel${sorted.length !== 1 ? 's' : ''} in ${activeBrandCity}`
      : `${brandHotelsData.length} hotel${brandHotelsData.length !== 1 ? 's' : ''}`;

  document.getElementById('brand-hotels-tbody').innerHTML = sorted.map(h => {
    const segColor = SEG_COLORS[h.category] || '#888888';
    return `<tr class="brand-hotel-row">
      <td class="hotel-name-cell"><button class="hotel-name-btn" onclick="showHotelDetail(${h.id})">${fmt.esc(h.name)}</button></td>
      <td>${fmt.esc(h.city)}</td>
      <td><span class="seg-pip" style="background:${segColor};margin-right:7px"></span>${fmt.esc(h.category)}</td>
      <td>${fmt.num(h.keys)}</td>
      <td>${fmt.pct(h.occupancy)}</td>
      <td>${fmt.mad(h.adr_mad)}</td>
      <td>${fmt.mad(h.revpar_mad)}</td>
      <td>${fmt.esc(h.owner || '—')}</td>
    </tr>`;
  }).join('');

  document.querySelectorAll('#brand-hotels-table .sortable-col').forEach(th => {
    const icon = th.querySelector('.sort-icon');
    th.classList.remove('sort-asc', 'sort-desc');
    if (th.dataset.bcol === col) {
      th.classList.add(dir === 1 ? 'sort-asc' : 'sort-desc');
      icon.textContent = dir === 1 ? '↑' : '↓';
    } else {
      icon.textContent = '↕';
    }
  });
}

function filterBrandHotelsByCity(city) {
  activeBrandCity = activeBrandCity === city ? null : city;
  updateBrandCityPills(activeBrandCity);
  renderBrandHotelsTable();
}

function updateBrandCityPills(activeCity) {
  document.querySelectorAll('#brand-cities-row .brand-city-pill').forEach(pill => {
    const pillCity = pill.dataset.city || null;
    pill.classList.toggle('active', pillCity === activeCity);
  });
}

function expandBrandCities(el) {
  const hidden = el.parentElement.querySelector('.brand-cities-hidden');
  if (!hidden) return;
  hidden.style.display = 'contents';
  const pills = hidden.querySelectorAll('.brand-city-pill');
  pills.forEach((pill, i) => {
    pill.style.opacity = '0';
    pill.style.transform = 'translateY(4px)';
    pill.style.transition = 'opacity 200ms ease, transform 200ms ease';
    setTimeout(() => {
      pill.style.opacity = '1';
      pill.style.transform = 'translateY(0)';
    }, i * 40);
  });
  el.remove();
}

// ─── Hotel detail ─────────────────────────────────────────────────

const OWNER_CONTEXT = {
  'Risma':        'Accor Morocco listed subsidiary (Bourse de Casablanca)',
  'Madaëf':       'CDG Group hospitality arm',
  'Royal':        'Royal Mansour Collection — Royal hospitality group',
  'Marchica Med': 'State-owned development agency',
  'Club Med':     'Club Med — owned by Fosun International',
};

async function showHotelDetail(id) {
  const h = hotels.find(x => +x.id === +id);
  if (!h) return;

  // Remember which screen we came from
  const active = document.querySelector('.screen.active');
  hotelDetailPrevScreen = active ? active.id.replace('screen-', '') : 'hotels';

  // Switch screen first so Chart.js canvas has visible dimensions
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById('screen-hotel').classList.add('active');
  setSidebar('hotel');

  // ── 1. Header ──
  document.getElementById('hotel-hd-name').textContent = h.name;
  document.getElementById('hotel-hd-sub').textContent =
    `${h.brand} · ${h.city} · ${h.category}`;

  const ownerLine = document.getElementById('hotel-hd-owner');
  if (h.owner && h.owner !== 'Undisclosed') {
    ownerLine.textContent = `Owner: ${h.owner}`;
    ownerLine.style.display = '';
  } else {
    ownerLine.style.display = 'none';
  }

  document.getElementById('hotel-hd-year').textContent =
    h.year_opened ? `Opened ${h.year_opened}` : '';

  const dqEl = document.getElementById('hotel-hd-dq');
  if ((h.data_quality || '').toLowerCase().startsWith('verified')) {
    dqEl.textContent = 'Verified';
    dqEl.className   = 'hotel-dq-badge dq-verified';
  } else {
    dqEl.textContent = 'Kōdō Estimate';
    dqEl.className   = 'hotel-dq-badge dq-estimate';
  }

  // ── 2. KPI cards ──
  const setKv = (id, v) => document.getElementById(id).querySelector('.kpi-value').textContent = v;
  setKv('hkpi-keys',   fmt.num(h.keys));
  setKv('hkpi-occ',    fmt.pct(h.occupancy));
  setKv('hkpi-adr',    fmt.mad(h.adr_mad));
  setKv('hkpi-revpar', fmt.mad(h.revpar_mad));

  // ── 3. Estimated financials (range model) ──
  renderHotelFinancials(h);

  // ── 4. Market context chart ──
  document.getElementById('hotel-ctx-city').textContent = h.city;
  renderHotelCityChart(h);

  // ── 5. Segment benchmarks ──
  renderHotelSegBench(h);

  // ── 6. Brand info ──
  const brandCount = hotels.filter(x => x.brand_group === h.brand_group).length;
  document.getElementById('hotel-brand-name').innerHTML = getBrandLogoImg(h.brand_group, 32) + ' ' + fmt.esc(h.brand_group);
  document.getElementById('hotel-brand-count').textContent = brandCount;
  const brandBtn = document.getElementById('hotel-brand-link');
  brandBtn.textContent     = `View all ${h.brand_group} properties →`;
  brandBtn.dataset.brand   = h.brand_group;

  // ── 7. Pipeline ──
  document.getElementById('hotel-pipe-city').textContent = h.city;
  await renderHotelPipeline(h);

  // ── 8. Owner section ──
  renderOwnerSection(h);

  // ── 9. Live Rate Intelligence ──
  renderRateCalendar(h.id);
  renderOccCalendar(h.id);
}

function renderHotelCityChart(h) {
  const cityHotels = hotels
    .filter(x => x.city === h.city)
    .sort((a, b) => b.revpar_mad - a.revpar_mad);

  const labels = cityHotels.map(x =>
    +x.id === +h.id ? `▶ ${x.name}` : x.name
  );
  const values = cityHotels.map(x => x.revpar_mad);
  const colors = cityHotels.map(() => getChartColors().barColor);

  const chartH = Math.max(200, cityHotels.length * 30 + 50);
  document.getElementById('hotel-city-chart-wrap').style.height = chartH + 'px';

  if (hotelCityChart) {
    hotelCityChart.data.labels                       = labels;
    hotelCityChart.data.datasets[0].data             = values;
    hotelCityChart.data.datasets[0].backgroundColor  = colors;
    hotelCityChart.update();
  } else {
    hotelCityChart = new Chart(
      document.getElementById('chart-hotel-city'),
      chartConfig(labels, values, ' MAD', colors, v => Math.round(v).toLocaleString('en'))
    );
  }
}

function renderHotelSegBench(h) {
  const peers = hotels.filter(x => x.city === h.city && x.category === h.category && +x.id !== +h.id);
  const bench  = document.getElementById('hotel-seg-bench');
  const ctxEl  = document.getElementById('hotel-bench-ctx');

  ctxEl.textContent = `${h.category} · ${h.city} average (${peers.length} peer${peers.length !== 1 ? 's' : ''})`;

  if (!peers.length) {
    bench.innerHTML = `<p class="hbench-no-peers">No comparable ${h.category} hotels in ${h.city}.</p>`;
    return;
  }

  const tk     = peers.reduce((s, x) => s + x.keys, 0);
  const ok     = peers.reduce((s, x) => s + x.keys * x.occupancy, 0);
  const avgOcc = ok / tk;
  const avgAdr = peers.reduce((s, x) => s + x.adr_mad * x.keys * x.occupancy, 0) / ok;
  const avgRev = peers.reduce((s, x) => s + x.revpar_mad * x.keys, 0) / tk;

  const metrics = [
    {
      label: 'Occupancy',
      mine: h.occupancy,     avg: avgOcc,
      fmtVal: v => fmt.pct(v),
      fmtDiff: d => (d >= 0 ? '+' : '') + (d * 100).toFixed(1) + ' pts',
      isPos: h.occupancy >= avgOcc,
    },
    {
      label: 'ADR (MAD)',
      mine: h.adr_mad,       avg: avgAdr,
      fmtVal: v => fmt.mad(v),
      fmtDiff: d => (d >= 0 ? '+' : '−') + 'MAD ' + fmt.mad(Math.abs(d)),
      isPos: h.adr_mad >= avgAdr,
    },
    {
      label: 'RevPAR (MAD)',
      mine: h.revpar_mad,    avg: avgRev,
      fmtVal: v => fmt.mad(v),
      fmtDiff: d => (d >= 0 ? '+' : '−') + 'MAD ' + fmt.mad(Math.abs(d)),
      isPos: h.revpar_mad >= avgRev,
    },
  ];

  bench.innerHTML = metrics.map(m => {
    const top      = Math.max(m.mine, m.avg) * 1.12 || 1;
    const mineW    = Math.round((m.mine / top) * 100);
    const avgW     = Math.round((m.avg  / top) * 100);
    const diff     = m.mine - m.avg;
    return `<div class="hbench-row">
      <div class="hbench-label">${m.label}</div>
      <div class="hbench-bars">
        <div class="hbench-bar-row">
          <span class="hbench-bar-lbl">This hotel</span>
          <div class="hbench-bar-track"><div class="hbench-bar-fill accent" style="width:${mineW}%"></div></div>
          <span class="hbench-val">${m.fmtVal(m.mine)}</span>
        </div>
        <div class="hbench-bar-row">
          <span class="hbench-bar-lbl">Peers avg</span>
          <div class="hbench-bar-track"><div class="hbench-bar-fill muted" style="width:${avgW}%"></div></div>
          <span class="hbench-val">${m.fmtVal(m.avg)}</span>
        </div>
      </div>
      <span class="hbench-diff ${m.isPos ? 'up' : 'down'}">${m.fmtDiff(diff)}</span>
    </div>`;
  }).join('');
}

async function renderHotelPipeline(h) {
  const content = document.getElementById('hotel-pipe-content');
  if (!pipelineData) {
    content.innerHTML = '<p class="hpipe-empty">Loading pipeline data…</p>';
    try {
      pipelineData = await fetch('/api/pipeline').then(r => r.json());
    } catch {
      content.innerHTML = '<p class="hpipe-empty">Pipeline data unavailable.</p>';
      return;
    }
  }

  const cityPipe = pipelineData.filter(p => p.city === h.city);
  if (!cityPipe.length) {
    content.innerHTML = `<p class="hpipe-empty">No confirmed pipeline in ${fmt.esc(h.city)}.</p>`;
    return;
  }

  const totalKeys = cityPipe.reduce((s, p) => s + p.keys, 0);
  const lastYear  = Math.max(...cityPipe.map(p => p.expected_opening));
  const items = cityPipe.map(p => `
    <div class="hpipe-item">
      <div class="hpipe-item-name">${fmt.esc(p.name)}</div>
      <span class="hpipe-item-meta">${fmt.esc(p.brand)} · ${p.keys || 'TBC'} keys · ${p.expected_opening}</span>
      <span class="${p.status === 'Under Construction' ? 'pipe-status-uc' : 'pipe-status-pl'}">${fmt.esc(p.status)}</span>
    </div>`).join('');

  content.innerHTML = `
    <p class="hpipe-summary">${totalKeys.toLocaleString('en')} new keys entering ${fmt.esc(h.city)} by ${lastYear}</p>
    <div class="hpipe-list">${items}</div>`;
}

function renderOwnerSection(h) {
  const section = document.getElementById('hotel-owner-section');
  if (!h.owner || h.owner === 'Undisclosed') {
    section.style.display = 'none';
    return;
  }
  section.style.display = '';
  document.getElementById('hotel-owner-name').textContent = h.owner;

  let ctx = '';
  for (const [key, val] of Object.entries(OWNER_CONTEXT)) {
    if (h.owner.includes(key)) { ctx = val; break; }
  }
  const ctxEl = document.getElementById('hotel-owner-ctx');
  if (ctx) {
    ctxEl.textContent     = ctx;
    ctxEl.style.display   = '';
  } else {
    ctxEl.style.display   = 'none';
  }
}

// ─── Rate Intelligence ─────────────────────────────────────────────────────────

const SOURCE_CLASS = {
  live_google:     'src-live-google',
  live_brand:      'src-live-brand',
  live_booking:    'src-live-booking',
  live_expedia:    'src-live-google',
  manual_override: 'src-manual-override',
  estimated:       'src-estimated',
  unavailable:     'src-unavailable',
};

const SOURCE_LABEL = {
  live_google:     'Google Hotels',
  live_brand:      'Brand Direct',
  live_booking:    'Booking.com',
  live_expedia:    'Expedia',
  manual_override: 'Manual Override',
  estimated:       'Kōdō Estimate',
  unavailable:     'Unavailable',
};

function fmtMadShort(v) {
  if (!v) return '—';
  const n = +v;
  if (n >= 1000) return `${(n/1000).toFixed(1)}k`;
  return String(Math.round(n));
}

function fmtMadLong(v) {
  if (!v) return '—';
  return `MAD ${(+v).toLocaleString()}`;
}

async function renderRateCalendar(hotelId) {
  const calEl    = document.getElementById('hrate-calendar');
  const badgeEl  = document.getElementById('hrate-source-badge');
  const updEl    = document.getElementById('hrate-updated');

  calEl.innerHTML = '<div class="bar-cal-loading">Loading rate data…</div>';

  let data;
  try {
    const resp = await fetch(`/api/rates?hotel_id=${hotelId}&days=35`);
    data = await resp.json();
  } catch (e) {
    calEl.innerHTML = '<div class="bar-cal-loading">Rate data unavailable</div>';
    return;
  }

  const rates   = data.rates || [];
  const sources = data.source_breakdown || {};

  // Build a map stay_date → rate row (prefer live over estimated)
  const rateMap = {};
  for (const r of rates) {
    const sd = r.stay_date;
    if (!rateMap[sd]) {
      rateMap[sd] = r;
    } else {
      const priority = {'live_google':5,'live_brand':5,'live_expedia':5,'manual_override':4,'live_booking':3,'estimated':1,'unavailable':0};
      if ((priority[r.source]||0) > (priority[rateMap[sd].source]||0)) rateMap[sd] = r;
    }
  }

  // Generate next 30 days
  const today = new Date();
  const cells  = [];
  for (let i = 1; i <= 30; i++) {
    const d   = new Date(today); d.setDate(today.getDate() + i);
    const iso = d.toISOString().split('T')[0];
    const r   = rateMap[iso] || null;
    cells.push({ iso, d, r });
  }

  // Dominant source for badge
  let dominantSrc = 'estimated';
  let maxCount = 0;
  for (const [src, cnt] of Object.entries(sources)) {
    if (cnt > maxCount && src !== 'unavailable') { maxCount = cnt; dominantSrc = src; }
  }
  badgeEl.textContent = `Source: ${SOURCE_LABEL[dominantSrc] || dominantSrc}`;

  if (data.last_scraped) {
    updEl.textContent = `Last updated: ${data.last_scraped} · Updates daily at 3:00 AM`;
  }

  // Build grid
  const DAYS = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
  let html = '';
  for (const { iso, d, r } of cells) {
    const src      = r ? r.source : 'unavailable';
    const cls      = SOURCE_CLASS[src] || 'src-estimated';
    const rateMAD  = r && r.rate_mad ? +r.rate_mad : null;
    const rateDisp = rateMAD ? fmtMadShort(rateMAD) : '—';
    const roomsLeft = r && r.rooms_left ? `<br>Rooms left: ${r.rooms_left}` : '';
    const tip = `${iso}<br>Rate: ${rateMAD ? fmtMadLong(rateMAD) : 'Unavailable'}<br>Source: ${SOURCE_LABEL[src]||src}${roomsLeft}`;
    html += `<div class="bar-cal-day ${cls}" title="">
      <div class="bar-cal-dn">${DAYS[d.getDay()]} ${d.getDate()}</div>
      <div class="bar-cal-rate">${rateDisp}</div>
      <div class="bar-cal-tip">${tip}</div>
    </div>`;
  }
  calEl.innerHTML = html;
}

function fmMad(n) {
  if (!n) return '—';
  n = +n;
  if (n >= 1_000_000_000) return `MAD ${(n/1e9).toFixed(1)}B`;
  if (n >= 1_000_000)     return `MAD ${(n/1e6).toFixed(1)}M`;
  return `MAD ${Math.round(n).toLocaleString()}`;
}

async function renderOccCalendar(hotelId) {
  const calEl   = document.getElementById('hocc-calendar');
  const badgeEl = document.getElementById('hocc-model-badge');
  const avgBar  = document.getElementById('hotel-cal-averages');
  const avgText = document.getElementById('hcal-avg-bar-text');
  const confEl  = document.getElementById('hcal-conf-note');

  calEl.innerHTML = '<div class="bar-cal-loading">Loading occupancy data…</div>';

  let data;
  try {
    const resp = await fetch(`/api/occupancy/${hotelId}`);
    if (!resp.ok) { calEl.innerHTML = '<div class="bar-cal-loading">Occupancy data unavailable</div>'; return; }
    data = await resp.json();
  } catch (e) {
    calEl.innerHTML = '<div class="bar-cal-loading">Occupancy data unavailable</div>';
    return;
  }

  const estimates = data.estimates || [];
  const estMap = {};
  for (const e of estimates) estMap[e.date] = e;

  const dark = !document.body.classList.contains('light');
  const dayNumCol = dark ? '#888888' : '#AAAAAA';

  const today = new Date();
  let html = '';
  for (let i = 1; i <= 30; i++) {
    const d   = new Date(today); d.setDate(today.getDate() + i);
    const iso = d.toISOString().split('T')[0];
    const e   = estMap[iso];
    const occ = e ? +e.estimated_occupancy : null;
    const conf = e ? e.confidence : 'low';

    let bg, col, fw = '', border = '';
    if (occ !== null) {
      if (dark) {
        if (occ >= 80) { bg = '#C8922A'; col = '#0A0A0A'; fw = '600'; }
        else if (occ >= 60) { bg = '#7A5818'; col = '#F0EDE6'; fw = '500'; }
        else { bg = '#1C1C1A'; col = '#888888'; border = '1px solid #7A5818'; }
      } else {
        if (occ >= 80) { bg = '#FDF3E0'; col = '#6B4A10'; fw = '600'; border = '1px solid #C8922A'; }
        else if (occ >= 60) { bg = '#FEF8EE'; col = '#8B6820'; border = '1px solid #E0B860'; }
        else { bg = '#FFFFFF'; col = '#8A8A8A'; border = '1px solid #ECECEC'; }
      }
    } else {
      bg = dark ? '#181818' : '#F8F8F8';
      col = dark ? '#444' : '#BBB';
      border = dark ? '1px dashed #333' : '1px dashed #DDD';
    }

    const styAttr = `background:${bg};color:${col};${fw ? `font-weight:${fw};` : ''}${border ? `border:${border};` : ''}`;
    const dispVal  = occ !== null ? `${occ.toFixed(0)}%` : '—';
    const confBadge = conf === 'high' ? '●' : conf === 'medium' ? '◑' : '○';
    const tip = e
      ? `${iso}\nOccupancy: ${occ.toFixed(1)}%\nConfidence: ${conf}\nBase: ${e.breakdown?.base ?? '—'}% + adj`
      : `${iso}\nNo estimate`;
    html += `<div class="bar-cal-day" style="${styAttr}" title="${tip}">
      <div class="bar-cal-dn" style="color:${dayNumCol};opacity:1">${d.getDate()}<span style="font-size:7px;margin-left:2px;opacity:0.6">${confBadge}</span></div>
      <div class="bar-cal-rate">${dispVal}</div>
    </div>`;
  }
  calEl.innerHTML = html;

  if (data.model_run_date) {
    badgeEl.textContent = `Model: ${data.model_run_date}`;
  }

  // Averages bar
  const cc = data.confidence_counts || {};
  if (data.avg_occupancy_30d != null) {
    const revStr = data.avg_revpar_30d ? ` · Est. RevPAR MAD ${Math.round(+data.avg_revpar_30d).toLocaleString()}` : '';
    avgText.textContent = `30-day averages: Est. Occupancy ${data.avg_occupancy_30d}%${revStr}`;
    confEl.textContent  = `High confidence: ${cc.high ?? 0} days · Medium: ${cc.medium ?? 0} · Low: ${cc.low ?? 0}`;
    avgBar.style.display = '';
  }
}

function renderHotelFinancials(h) {
  const MULTIPLES = {
    'Ultra Luxury':  { lo: 18, hi: 22 },
    'Luxury':        { lo: 15, hi: 18 },
    'Upper Upscale': { lo: 12, hi: 15 },
    'Upscale':       { lo: 10, hi: 12 },
    'Midscale':      { lo:  8, hi: 10 },
    'Economy':       { lo:  6, hi:  8 },
  };

  const bar  = h.adr_mad;
  const occ  = h.occupancy;
  const keys = h.keys;

  const occLo = Math.max(0.10, occ - 0.08);
  const occHi = Math.min(0.98, occ + 0.08);

  const revLoM = bar * occLo * keys * 365 / 1e6;
  const revHiM = bar * occHi * keys * 365 / 1e6;

  const mult = MULTIPLES[h.category] || { lo: 8, hi: 12 };

  const assetLoM = revLoM * mult.lo;
  const assetHiM = revHiM * mult.hi;

  const vpkLoMad = (assetLoM * 1e6) / keys;
  const vpkHiMad = (assetHiM * 1e6) / keys;

  const fmM  = v => `MAD ${v.toFixed(1)}M`;
  const fmLg = v => v >= 1000 ? `MAD ${(v / 1000).toFixed(1)}B` : `MAD ${v.toFixed(0)}M`;
  const fmK  = v => v >= 1e6  ? `MAD ${(v / 1e6).toFixed(1)}M`  : `MAD ${(v / 1000).toFixed(0)}k`;
  const fmEur = v => `EUR ${Math.round(v / 10.8 / 1000)}k`;

  document.getElementById('hfin-rev-range').textContent =
    `${fmM(revLoM)} — ${fmM(revHiM)}`;
  document.getElementById('hfin-rev-sub').textContent =
    `Based on BAR × occupancy range × ${keys} keys × 365 days`;

  document.getElementById('hfin-asset-range').textContent =
    `${fmLg(assetLoM)} — ${fmLg(assetHiM)}`;
  document.getElementById('hfin-asset-sub').textContent =
    `Based on ${mult.lo}×–${mult.hi}× rooms revenue multiple (${h.category} segment)`;

  document.getElementById('hfin-vpk-range').textContent =
    `${fmK(vpkLoMad)} — ${fmK(vpkHiMad)} / ${fmEur(vpkLoMad)} — ${fmEur(vpkHiMad)}`;
  document.getElementById('hfin-vpk-sub').textContent =
    `EUR at MAD/EUR 10.8 conversion`;

  document.getElementById('hfin-confidence-badge').textContent =
    'Medium · Based on Kōdō static estimates';
}


// ─── Map ──────────────────────────────────────────────────────────

function markerRadius(h) {
  return Math.max(8, Math.sqrt(h.keys) * 0.78);
}

function popupHTML(h) {
  return `
    <div class="hiq-popup">
      <button class="hiq-popup-name-btn" onclick="showHotelDetail(${h.id})">${fmt.esc(h.name)}</button>
      <div class="hiq-popup-meta">${fmt.esc(h.brand)} · ${fmt.esc(h.category)} · ${h.year_opened}</div>
      <div class="hiq-popup-grid">
        <div class="hiq-popup-stat">
          <div class="hiq-popup-stat-val">${fmt.num(h.keys)}</div>
          <div class="hiq-popup-stat-lbl">Keys</div>
        </div>
        <div class="hiq-popup-stat">
          <div class="hiq-popup-stat-val">${fmt.pct(h.occupancy)}</div>
          <div class="hiq-popup-stat-lbl">Occupancy</div>
        </div>
        <div class="hiq-popup-stat">
          <div class="hiq-popup-stat-val">${fmt.mad(h.adr_mad)}</div>
          <div class="hiq-popup-stat-lbl">ADR MAD</div>
        </div>
        <div class="hiq-popup-stat">
          <div class="hiq-popup-stat-val">${fmt.mad(h.revpar_mad)}</div>
          <div class="hiq-popup-stat-lbl">RevPAR MAD</div>
        </div>
      </div>
      <button class="hiq-popup-profile-btn" onclick="showHotelDetail(${h.id})">View full profile →</button>
    </div>`;
}

// ─── Google Maps ──────────────────────────────────────────────────

const GMAP_OPTIONS_BASE = {
  mapTypeId:          'roadmap',
  mapTypeControl:     false,
  streetViewControl:  false,
  fullscreenControl:  false,
  zoomControl:        true,
  restriction: {
    latLngBounds: { north: 37, south: 20, west: -18, east: 1 },
    strictBounds: false,
  },
};

// Called by Google Maps API when it finishes loading
function initGoogleMaps() {
  googleMapsApiReady = true;
  // Re-trigger if map screen is already visible
  if (document.getElementById('screen-map')?.classList.contains('active') && !googleMap) {
    initMap();
  }
}

function swapMapTheme(mode) {
  const styles = mode === 'light' ? GMAP_STYLE_LIGHT : GMAP_STYLE_DARK;
  if (googleMap)         googleMap.setOptions({ styles });
  if (googlePipelineMap) googlePipelineMap.setOptions({ styles });
}

function initMap() {
  if (!googleMapsApiReady || googleMap || !hotels) return;
  try {
    const isDark = !document.body.classList.contains('light');
    googleMap = new google.maps.Map(document.getElementById('map-container'), {
      ...GMAP_OPTIONS_BASE,
      center: { lat: 31.5, lng: -5.5 },
      zoom:   6,
      styles: isDark ? GMAP_STYLE_DARK : GMAP_STYLE_LIGHT,
    });

    hotelMarkers = hotels.map(h => {
      const marker = new google.maps.Marker({
        position: { lat: h.lat, lng: h.lng },
        map:      googleMap,
        icon: {
          path:        google.maps.SymbolPath.CIRCLE,
          scale:       markerRadius(h),
          fillColor:   SEG_COLORS[h.category] || '#888888',
          fillOpacity: 0.85,
          strokeColor: 'rgba(255,255,255,0.6)',
          strokeWeight: 1.2,
        },
      });
      marker.addListener('click', () => {
        if (activeInfoWindow) activeInfoWindow.close();
        activeInfoWindow = new google.maps.InfoWindow({ content: popupHTML(h) });
        activeInfoWindow.open({ map: googleMap, anchor: marker });
      });
      return { marker, hotel: h };
    });

    updateMapMarkers();
  } catch (e) {
    console.error('Google Maps init failed:', e);
  }
}

function updateMapMarkers() {
  if (!googleMap) return;
  let visible = 0;
  hotelMarkers.forEach(({ marker, hotel: h }) => {
    const show = (state.city   === 'all' || h.city     === state.city) &&
                 (state.mapSeg === 'all' || h.category === state.mapSeg);
    marker.setMap(show ? googleMap : null);
    if (show) visible++;
  });
  const countEl = document.getElementById('map-count');
  if (countEl) countEl.textContent = visible + ' hotel' + (visible !== 1 ? 's' : '');
}

function panMap() {
  if (!googleMap) return;
  if (state.city === 'all') {
    googleMap.setCenter({ lat: 31.5, lng: -5.5 });
    googleMap.setZoom(6);
  } else {
    const cityHotels = hotels.filter(h => h.city === state.city);
    if (cityHotels.length) {
      const lat = cityHotels.reduce((s, h) => s + h.lat, 0) / cityHotels.length;
      const lng = cityHotels.reduce((s, h) => s + h.lng, 0) / cityHotels.length;
      googleMap.setCenter({ lat, lng });
      googleMap.setZoom(10);
    }
  }
}

// ─── Hotels screen ────────────────────────────────────────────────

const STRING_COLS = new Set(['name', 'city', 'category', 'brand_group', 'brand']);

const hotelsState = {
  query: '',
  city:  'all',
  seg:   'all',
  owner: 'all',
  col:   'revpar_mad',
  dir:   -1,
};

function filterHotels() {
  const q = hotelsState.query.trim().toLowerCase();
  return (hotels || []).filter(h => {
    if (hotelsState.city  !== 'all' && h.city     !== hotelsState.city)  return false;
    if (hotelsState.seg   !== 'all' && h.category !== hotelsState.seg)   return false;
    if (hotelsState.owner !== 'all' && h.owner    !== hotelsState.owner) return false;
    if (q) {
      const haystack = [h.name, h.city, h.brand, h.brand_group, h.owner].join(' ').toLowerCase();
      if (!haystack.includes(q)) return false;
    }
    return true;
  });
}

function sortHotels(list) {
  const { col, dir } = hotelsState;
  return [...list].sort((a, b) => {
    const va = a[col], vb = b[col];
    if (STRING_COLS.has(col)) return dir * String(va).localeCompare(String(vb));
    return dir * (va - vb);
  });
}

function syncHotelsSortIcons() {
  document.querySelectorAll('#hotels-table .sortable-col').forEach(th => {
    const icon = th.querySelector('.sort-icon');
    if (!icon) return;
    th.classList.remove('sort-asc', 'sort-desc');
    if (th.dataset.col === hotelsState.col) {
      th.classList.add(hotelsState.dir === 1 ? 'sort-asc' : 'sort-desc');
      icon.textContent = hotelsState.dir === 1 ? '↑' : '↓';
    } else {
      icon.textContent = '↕';
    }
  });
  const sel = document.getElementById('hotels-sort-select');
  if (sel && sel.querySelector(`option[value="${hotelsState.col}"]`)) sel.value = hotelsState.col;
}

function renderActiveHotelsFilters() {
  const chips = [];
  if (hotelsState.city  !== 'all') chips.push({ type: 'city',  label: hotelsState.city });
  if (hotelsState.seg   !== 'all') chips.push({ type: 'seg',   label: hotelsState.seg });
  if (hotelsState.owner !== 'all') chips.push({ type: 'owner', label: hotelsState.owner });
  if (hotelsState.query)           chips.push({ type: 'query', label: `"${hotelsState.query}"` });

  const row     = document.getElementById('hotels-active-filters');
  const chipsEl = document.getElementById('hotels-filter-chips');
  const clearEl = document.getElementById('hotels-clear-all');
  if (!chips.length) { row.classList.remove('visible'); return; }
  row.classList.add('visible');
  chipsEl.innerHTML = chips.map(c =>
    `<span class="filter-chip" data-ftype="${c.type}">${fmt.esc(c.label)}<button class="filter-chip-remove" aria-label="Remove">×</button></span>`
  ).join('');
  clearEl.style.display = chips.length > 1 ? '' : 'none';
}

function clearAllHotelsFilters() {
  hotelsState.query = '';
  hotelsState.city  = 'all';
  hotelsState.seg   = 'all';
  hotelsState.owner = 'all';
  const searchEl = document.getElementById('hotels-search');
  if (searchEl) { searchEl.value = ''; }
  const clearBtn = document.getElementById('hotels-search-clear');
  if (clearBtn) clearBtn.classList.remove('visible');
  const ownerSel = document.getElementById('hotels-owner-select');
  if (ownerSel) ownerSel.value = 'all';
  document.querySelectorAll('#hotels-city-pills .pill').forEach(p =>
    p.classList.toggle('active', p.dataset.hcity === 'all'));
  document.querySelectorAll('#hotels-seg-pills .pill').forEach(p =>
    p.classList.toggle('active', p.dataset.hseg === 'all'));
  renderHotelsTable();
}

function renderHotelsTable() {
  if (!hotels) return;
  const filtered = filterHotels();
  const sorted   = sortHotels(filtered);
  const total    = hotels.length;

  const filteredCities = new Set(filtered.map(h => h.city)).size;
  document.getElementById('hotels-sub').textContent =
    `${filtered.length} hotel${filtered.length !== 1 ? 's' : ''} · ${filteredCities} ${filteredCities !== 1 ? 'cities' : 'city'} · All performance: Kōdō estimates 2025`;

  const countEl = document.getElementById('hotels-results-count');
  if (countEl) countEl.textContent = `Showing ${sorted.length} of ${total} hotels`;

  const tbody = document.getElementById('hotels-tbody');
  if (!sorted.length) {
    tbody.innerHTML = `<tr><td colspan="9"><div class="table-empty-state">
      <p class="table-empty-title">No hotels match your filters</p>
      <p class="table-empty-sub">Try adjusting your search or clearing filters</p>
      <button class="btn btn-ghost" onclick="clearAllHotelsFilters()" style="font-size:12px;padding:6px 16px">Clear all filters</button>
    </div></td></tr>`;
  } else {
    tbody.innerHTML = sorted.map(h => {
      const segColor  = SEG_COLORS[h.category] || '#888888';
      return `<tr class="hotel-row-link" onclick="showHotelDetail(${h.id})">
        <td class="hotel-name-cell"><button class="hotel-name-btn">${fmt.esc(h.name)}</button></td>
        <td>${fmt.esc(h.city)}</td>
        <td class="col-hide-mobile"><span class="seg-pip" style="background:${segColor};margin-right:7px"></span>${fmt.esc(h.category)}</td>
        <td class="col-hide-mobile">${getBrandLogoImg(h.brand_group, 16)} ${fmt.esc(h.brand_group)}</td>
        <td class="col-hide-mobile">${fmt.num(h.keys)}</td>
        <td class="col-hide-mobile">${fmt.pct(h.occupancy)}</td>
        <td class="col-hide-mobile">${fmt.mad(h.adr_mad)}</td>
        <td>${fmt.mad(h.revpar_mad)}</td>
      </tr>`;
    }).join('');
  }

  document.getElementById('hotels-footer').textContent =
    `Showing ${sorted.length} of ${total} hotel${total !== 1 ? 's' : ''}`;

  syncHotelsSortIcons();
  renderActiveHotelsFilters();
}

// ─── Full render ──────────────────────────────────────────────────

function render() {
  renderKPIs();
  renderCharts();
  renderBrandTable();
  if (googleMap) {
    updateMapMarkers();
    panMap();
  }
}

// ─── Redraw all charts on theme change ────────────────────────────

function redrawChartsForTheme() {
  // Dashboard bar charts
  if (revChart) { revChart.destroy(); revChart = null; }
  if (occChart)  { occChart.destroy();  occChart = null; }
  if (hotels) renderCharts();

  // Pipeline charts
  if (pipelineChartProj) { pipelineChartProj.destroy(); pipelineChartProj = null; }
  if (pipelineChartCity) { pipelineChartCity.destroy(); pipelineChartCity = null; }
  if (pipelineInited && pipelineData) renderPipelineCharts();

  // Tourism charts — destroy and reset flag; reinit if screen is active
  if (tourismInited) {
    ['chart-tour-arrivals','chart-tour-transport','chart-tour-origins',
     'chart-tour-nights','chart-tour-airports','chart-tour-revenue','chart-tour-season',
    ].forEach(id => { const c = Chart.getChart(id); if (c) c.destroy(); });
    tourismInited = false;
    const tourismEl = document.getElementById('screen-tourism');
    if (tourismEl && tourismEl.classList.contains('active')) {
      initTourismCharts();
    }
  }

  // Benchmarking trend + DOW charts
  if (benchTrendRevpar) { benchTrendRevpar.destroy(); benchTrendRevpar = null; }
  if (benchTrendOcc)    { benchTrendOcc.destroy();    benchTrendOcc    = null; }
  if (benchDOWChart)    { benchDOWChart.destroy();     benchDOWChart    = null; }
  if (benchmarkInited && benchmarkData) { renderBenchTrends(); renderBenchDOW(); }

  // Brand detail chart — recreate if screen is currently visible
  if (brandChart) { brandChart.destroy(); brandChart = null; }
  const brandScreen = document.getElementById('screen-brand');
  if (brandScreen && brandScreen.classList.contains('active') && brandHotelsData.length) {
    const cityData = cityAggs(brandHotelsData).sort((a, b) => b.revpar_mad - a.revpar_mad);
    const labels = cityData.map(c => c.city);
    const values = cityData.map(c => c.revpar_mad);
    document.getElementById('brand-chart-wrap').style.height = Math.max(240, labels.length * 38 + 50) + 'px';
    brandChart = new Chart(
      document.getElementById('chart-brand-revpar'),
      chartConfig(labels, values, ' MAD', labels.map(() => getChartColors().barColor), v => Math.round(v).toLocaleString('en'))
    );
  }

  // Hotel city chart — recreate if screen is currently visible
  if (hotelCityChart) { hotelCityChart.destroy(); hotelCityChart = null; }
  const hotelScreen = document.getElementById('screen-hotel');
  if (hotelScreen && hotelScreen.classList.contains('active') && hotels) {
    const nameEl = document.getElementById('hotel-hd-name');
    const h = nameEl && hotels.find(x => x.name === nameEl.textContent);
    if (h) renderHotelCityChart(h);
  }
}

// ─── Tourism screen ───────────────────────────────────────────────

const TOUR_EVENTS = [
  { city:'Marrakech',  name:'Marrakech Marathon',                    date:'January 2026',     attendance:'10,000+ runners',      type:'Sport',     desc:'Annual international marathon through the medina and palm groves.' },
  { city:'Rabat',      name:'Rabat International Fashion Week',      date:'March 2026',        attendance:'',                     type:'Culture',   desc:'Emerging designers showcase alongside established North African labels.' },
  { city:'Casablanca', name:'Morocco Traders Summit',                date:'March 2026',        attendance:'5,000 delegates',      type:'Business',  desc:'Annual trade and investment summit for North Africa and the MENA region.' },
  { city:'National',   name:'Eid Al Fitr 2026',                      date:'c. 30 March 2026',  attendance:'National',             type:'Religious', desc:'End of Ramadan — nationwide celebration; peak domestic travel period.' },
  { city:'Casablanca', name:'Casablanca Finance City Forum',         date:'April 2026',        attendance:'3,000 delegates',      type:'Business',  desc:'CFC flagship event bringing together African financial leaders.' },
  { city:'Agadir',     name:'International Agadir Fishing Festival', date:'April 2026',        attendance:'',                     type:'Culture',   desc:'Annual festival celebrating the city\'s coastal fishing heritage.' },
  { city:'Fes',        name:'SIAM International Agriculture Fair',   date:'April 2026',        attendance:'1M+ visitors',         type:'Business',  desc:'Africa\'s leading agricultural exhibition, held at Meknès–Fes.' },
  { city:'Agadir',     name:'Agadir Beach Soccer World Cup',         date:'May 2026',          attendance:'',                     type:'Sport',     desc:'FIFA-recognised beach soccer tournament on the Agadir seafront.' },
  { city:'Rabat',      name:'Mawazine Festival',                     date:'May–June 2026',     attendance:'2M+ total',            type:'Mega',      desc:'One of the world\'s largest music festivals by total attendance.' },
  { city:'Fes',        name:'Fes Festival of World Sacred Music',    date:'June 2026',         attendance:'80,000',               type:'Music',     desc:'Internationally acclaimed spiritual music festival in the ancient medina.' },
  { city:'Essaouira',  name:'Gnaoua World Music Festival',           date:'June 2026',         attendance:'450,000+ over 4 days', type:'Music',     desc:'UNESCO-endorsed Gnaoua and world music festival on the Atlantic coast.' },
  { city:'National',   name:'Eid Al Adha 2026',                      date:'c. 6–7 June 2026',  attendance:'National',             type:'Religious', desc:'Feast of Sacrifice — major national holiday with high domestic movement.' },
  { city:'Marrakech',  name:'Atlas Weekend',                         date:'July 2026',         attendance:'30,000',               type:'Music',     desc:'Multi-genre festival drawing international and regional acts.' },
  { city:'Agadir',     name:'Timitar Festival',                      date:'July 2026',         attendance:'300,000+',             type:'Music',     desc:'Amazigh world music festival, one of Morocco\'s largest by attendance.' },
  { city:'Dakhla',     name:'Dakhla Atlantic Festival',              date:'July 2026',         attendance:'',                     type:'Culture',   desc:'Arts and music celebration on the Atlantic coast of southern Morocco.' },
  { city:'Tanger',     name:'Tanger International Festival',         date:'August 2026',       attendance:'',                     type:'Culture',   desc:'Arts and culture festival at the Cervantes Theatre and open-air venues.' },
  { city:'Dakhla',     name:'Dakhla Kitesurfing World Cup',          date:'August 2026',       attendance:'5,000+',               type:'Sport',     desc:'IKA World Tour stop on the Dakhla lagoon, one of the top kite venues.' },
  { city:'Tanger',     name:'Tanger Med Business Forum',             date:'September 2026',    attendance:'',                     type:'Business',  desc:'Annual forum on port logistics, trade, and Mediterranean economies.' },
  { city:'National',   name:'Aid Al Mawlid 2026',                    date:'September 2026',    attendance:'National',             type:'Religious', desc:'Prophet\'s birthday — observed nationwide; elevated domestic travel.' },
  { city:'Marrakech',  name:'Oasis Festival',                        date:'October 2026',      attendance:'25,000',               type:'Music',     desc:'Electronic music and arts festival set at the Atlas Studios.' },
  { city:'Marrakech',  name:'Marrakech International Film Festival', date:'November 2026',     attendance:'50,000+',              type:'Culture',   desc:'Premier film festival showcasing African and world cinema.' },
  { city:'Marrakech',  name:'Marrakech Airshow',                     date:'2026 (TBC)',         attendance:'TBC',                  type:'Business',  desc:'Biennial aerospace trade exhibition and air display.' },
];

const EVENT_TYPE_CLASS = {
  Sport: 'etype-sport', Culture: 'etype-culture', Music: 'etype-music',
  Business: 'etype-business', Religious: 'etype-religious', Mega: 'etype-mega',
};

const EVENT_DOT_COLORS = {
  Sport: '#B87860', Culture: '#A06848', Music: '#C89070',
  Business: '#886050', Religious: '#D0A888', Mega: '#B87860',
};

function parseEventDate(dateStr) {
  const MONTH_NUM = {January:1,February:2,March:3,April:4,May:5,June:6,July:7,August:8,September:9,October:10,November:11,December:12};
  const MONTH_ABB = ['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  // "Month–Month Year" range
  const rng = dateStr.match(/^(\w+)[–\-](\w+)\s+\d{4}/);
  if (rng && MONTH_NUM[rng[1]]) {
    const m1 = MONTH_NUM[rng[1]], m2 = MONTH_NUM[rng[2]];
    return { sortKey: m1 * 100, month: MONTH_ABB[m1], day: '', range: `${MONTH_ABB[m1]}–${MONTH_ABB[m2]}` };
  }
  // "c. D–D Month Year" or "c. D Month Year"
  const approx = dateStr.match(/c\.\s*(\d{1,2})(?:[–\-](\d{1,2}))?\s+(\w+)\s+\d{4}/);
  if (approx && MONTH_NUM[approx[3]]) {
    const m = MONTH_NUM[approx[3]];
    const day = approx[2] ? `${approx[1]}–${approx[2]}` : approx[1];
    return { sortKey: m * 100 + parseInt(approx[1]), month: MONTH_ABB[m], day, range: '' };
  }
  // "Month Year"
  for (const [name, num] of Object.entries(MONTH_NUM)) {
    if (dateStr.includes(name)) {
      return { sortKey: num * 100, month: MONTH_ABB[num], day: '', range: '' };
    }
  }
  return { sortKey: 9999, month: 'TBC', day: '', range: '' };
}

let eventsFilter = 'all';

function renderTourismEvents() {
  const filtered = eventsFilter === 'all' ? TOUR_EVENTS : TOUR_EVENTS.filter(ev => ev.city === eventsFilter);
  const sorted = [...filtered].sort((a, b) => parseEventDate(a.date).sortKey - parseEventDate(b.date).sortKey);

  if (!sorted.length) {
    document.getElementById('events-container').innerHTML =
      '<p style="padding:24px 20px;font-family:\'Plus Jakarta Sans\',sans-serif;font-size:13px;color:var(--text-muted)">No events for this selection.</p>';
    return;
  }

  document.getElementById('events-container').innerHTML = `<div class="timeline-container">${
    sorted.map((ev, i) => {
      const pd = parseEventDate(ev.date);
      const dotColor = EVENT_DOT_COLORS[ev.type] || 'var(--border-light)';
      const isMega = ev.type === 'Mega';

      const dateColHtml = pd.range
        ? `<span class="timeline-date__month">${pd.month}</span><span class="timeline-date__range">${pd.range}</span>`
        : pd.day
        ? `<span class="timeline-date__month">${pd.month}</span><span class="timeline-date__day">${pd.day}</span>`
        : `<span class="timeline-date__month">${pd.month}</span>`;

      const dotStyle = isMega
        ? `style="width:14px;height:14px;margin-top:4px;background:${dotColor};border:none;"`
        : `style="border-color:${dotColor};"`;

      const showAttendance = ev.attendance && ev.attendance !== 'TBC' && ev.attendance !== 'National';
      const attendanceHtml = showAttendance
        ? `<span class="timeline-attendance">↗ <span class="timeline-attendance__num">${fmt.esc(ev.attendance)}</span></span>`
        : '';
      const cityTagHtml = eventsFilter === 'all'
        ? `<span class="timeline-city-tag">${fmt.esc(ev.city === 'National' ? 'Nationwide' : ev.city)}</span>`
        : '';
      const hasMeta = showAttendance || eventsFilter === 'all';

      return `<div class="timeline-item">
        <div class="timeline-date">${dateColHtml}</div>
        <div class="timeline-spine">
          <div class="timeline-spine__line"></div>
          <div class="timeline-dot${isMega ? ' timeline-dot--mega' : ''}" ${dotStyle}></div>
        </div>
        <div class="timeline-content">
          <div class="timeline-event-title">${fmt.esc(ev.name)}</div>
          <span class="event-type-pill ${EVENT_TYPE_CLASS[ev.type] || ''}" style="margin-bottom:8px;display:inline-block;">${fmt.esc(ev.type)}</span>
          ${ev.desc ? `<div class="timeline-detail">${fmt.esc(ev.desc)}</div>` : ''}
          ${hasMeta ? `<div class="timeline-meta">${attendanceHtml}${cityTagHtml}</div>` : ''}
        </div>
      </div>`;
    }).join('')
  }</div>`;
}

const TOUR_NIGHTS_DATA = {
  labels: ['Other','Essaouira','Tanger','Fes','Casablanca','Agadir','Marrakech'],
  years: {
    2021: [2.8, 0.6, 1.1, 1.4, 2.8, 6.2, 8.1],
    2022: [4.8, 1.0, 1.8, 2.2, 4.2, 9.1, 12.4],
    2023: [6.1, 1.2, 2.2, 2.9, 5.1, 10.8, 15.2],
    2024: [6.8, 1.4, 2.5, 3.2, 5.7, 11.6, 16.8],
    2025: [7.3, 1.6, 2.8, 3.6, 6.2, 12.4, 18.2],
  },
};

const TOUR_AIRPORT_DATA = {
  labels: ['Nador NDR','Oujda OUD','Rabat RBA','Fes FEZ','Tanger TNG','Agadir AGA','Marrakech RAK','Casablanca CMN'],
  years: {
    2021: [0.2, 0.3, 0.4, 0.6, 0.8, 1.2, 2.1, 4.2],
    2022: [0.4, 0.5, 0.7, 1.1, 1.4, 2.1, 4.2, 7.8],
    2023: [0.5, 0.6, 0.9, 1.4, 1.7, 2.8, 5.6, 9.4],
    2024: [0.55, 0.7, 1.0, 1.6, 1.9, 3.1, 6.2, 10.6],
    2025: [0.6, 0.8, 1.1, 1.8, 2.1, 3.4, 6.8, 11.2],
  },
};

const TOUR_ORIGINS_DATA = {
  labels: ['France','MRE','Spain','UK','Germany','Gulf States','USA','Italy','Other'],
  years: {
    2021: [24, 20, 12, 9, 7, 5, 4, 3, 16],
    2022: [23, 19, 13, 10, 7, 6, 4, 3, 15],
    2023: [23, 18, 14, 10, 8, 6, 5, 4, 12],
    2024: [22, 18, 14, 10, 8, 7, 5, 4, 12],
    2025: [22, 18, 14, 10, 8, 7, 5, 4, 12],
  },
};

function initTourismCharts() {
  if (tourismInited) return;

  // Set chart-wrap height: also zeroes min-height so CSS 360px default doesn't interfere
  const setH = (id, h) => {
    const el = document.getElementById(id);
    el.style.minHeight = '0';
    el.style.height = h + 'px';
  };

  const addYearTabs = (canvasId, data) => {
    const canvas = document.getElementById(canvasId);
    const wrap = canvas.closest('.chart-wrap');
    const tabsDiv = document.createElement('div');
    tabsDiv.className = 'chart-year-tabs';
    [2021, 2022, 2023, 2024, 2025].forEach(yr => {
      const btn = document.createElement('button');
      btn.className = 'chart-year-tab' + (yr === 2025 ? ' active' : '');
      btn.textContent = yr;
      btn.addEventListener('click', () => {
        tabsDiv.querySelectorAll('.chart-year-tab').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const chart = Chart.getChart(canvas);
        if (chart) { chart.data.datasets[0].data = data.years[yr]; chart.update(); }
      });
      tabsDiv.appendChild(btn);
    });
    wrap.parentNode.insertBefore(tabsDiv, wrap);
  };

  // ── Helper for vertical bar charts ──────────────────────────────
  function vBar(labels, values, bgColors, lblFmt, tipFmt) {
    const cc = getChartColors();
    return {
      type: 'bar',
      data: { labels, datasets: [{ data: values, backgroundColor: bgColors, hoverBackgroundColor: getChartColors().hoverColor, borderRadius: 4, borderSkipped: false }] },
      options: {
        responsive: true, maintainAspectRatio: false, animation: { duration: 350 },
        layout: { padding: { top: 28 } },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: cc.tooltipBg, borderColor: cc.tooltipBdr, borderWidth: 1,
            titleColor: cc.tooltipTtl, bodyColor: cc.tooltipBdy,
            padding: { top: 8, bottom: 8, left: 12, right: 12 },
            callbacks: { label: ctx => '  ' + tipFmt(ctx.raw) },
          },
          datalabels: {
            anchor: 'end', align: 'top', clip: false,
            color: cc.label, font: { size: 11, weight: '600' },
            padding: { bottom: 2 }, formatter: lblFmt,
          },
        },
        scales: {
          x: { ticks: { color: cc.tick, font: { size: 11 } } },
          y: { ticks: { color: cc.tick, font: { size: 11 } } },
        },
      },
    };
  }

  // 1. International Arrivals Trend
  setH('twrap-arrivals', 290);
  const arrLbls = ['2020','2021','2022','2023','2024','2025','2026E'];
  const arrVals = [2.3, 5.2, 11.0, 14.5, 17.4, 20.1, 22.5];
  new Chart(document.getElementById('chart-tour-arrivals'),
    vBar(arrLbls, arrVals, arrLbls.map(() => getChartColors().barColor),
      v => v + 'M', v => v + 'M arrivals'));

  // 2. Arrivals by Mode of Transport (grouped)
  setH('twrap-transport', 290);
  {
    const cc = getChartColors();
    new Chart(document.getElementById('chart-tour-transport'), {
      type: 'bar',
      data: {
        labels: ['2022','2023','2024','2025','2026E'],
        datasets: [
          { label: 'Air',  data: [7.2, 9.8, 12.1, 14.2, 15.8], backgroundColor: getChartColors().barColor, borderRadius: 3, borderSkipped: false },
          { label: 'Sea',  data: [2.8, 3.2,  3.8,  4.1,  4.6], backgroundColor: '#456B38',         borderRadius: 3, borderSkipped: false },
          { label: 'Land', data: [1.0, 1.5,  1.5,  1.8,  2.1], backgroundColor: '#705040',          borderRadius: 3, borderSkipped: false },
        ],
      },
      options: {
        responsive: true, maintainAspectRatio: false, animation: { duration: 350 },
        layout: { padding: { top: 12 } },
        plugins: {
          legend: { display: false },
          datalabels: { display: false },
          tooltip: {
            backgroundColor: cc.tooltipBg, borderColor: cc.tooltipBdr, borderWidth: 1,
            titleColor: cc.tooltipTtl, bodyColor: cc.tooltipBdy,
            callbacks: { label: ctx => `  ${ctx.dataset.label}: ${ctx.raw}M` },
          },
        },
        scales: {
          x: { ticks: { color: cc.tick, font: { size: 11 } } },
          y: { ticks: { color: cc.tick, font: { size: 11 } } },
        },
      },
    });
  }

  // 3. Origin Markets (horizontal, with year tabs)
  const origLbls = TOUR_ORIGINS_DATA.labels;
  const origVals = TOUR_ORIGINS_DATA.years[2025];
  setH('twrap-origins', Math.max(260, origLbls.length * 34 + 50));
  const origCfg = chartConfig(origLbls, origVals, '%', origLbls.map(() => getChartColors().barColor), v => v + '%');
  origCfg.options.plugins.tooltip.callbacks.label = ctx => '  ' + ctx.raw + '%';
  new Chart(document.getElementById('chart-tour-origins'), origCfg);
  addYearTabs('chart-tour-origins', TOUR_ORIGINS_DATA);

  // 4. Tourist Nights by Destination (horizontal, sorted asc so Marrakech is top, with year tabs)
  const nightsLbls = TOUR_NIGHTS_DATA.labels;
  const nightsVals = TOUR_NIGHTS_DATA.years[2025];
  setH('twrap-nights', Math.max(240, nightsLbls.length * 34 + 50));
  const nightsCfg = chartConfig(nightsLbls, nightsVals, 'M', nightsLbls.map(() => getChartColors().barColor), v => v + 'M');
  nightsCfg.options.plugins.tooltip.callbacks.label = ctx => '  ' + ctx.raw + 'M nights';
  new Chart(document.getElementById('chart-tour-nights'), nightsCfg);
  addYearTabs('chart-tour-nights', TOUR_NIGHTS_DATA);

  // 5. Airport Traffic (horizontal, sorted asc so CMN is top, with year tabs)
  const airLbls = TOUR_AIRPORT_DATA.labels;
  const airVals  = TOUR_AIRPORT_DATA.years[2025];
  setH('twrap-airports', Math.max(260, airLbls.length * 34 + 50));
  const airCfg = chartConfig(airLbls, airVals, 'M pax', airLbls.map(() => getChartColors().barColor), v => v + 'M');
  airCfg.options.plugins.tooltip.callbacks.label = ctx => '  ' + ctx.raw + 'M passengers';
  new Chart(document.getElementById('chart-tour-airports'), airCfg);
  addYearTabs('chart-tour-airports', TOUR_AIRPORT_DATA);

  // 6. Tourism Revenue Trend
  setH('twrap-revenue', 290);
  const revLbls = ['2020','2021','2022','2023','2024','2025','2026E'];
  const revVals = [34, 44, 76, 89, 105, 118, 132];
  new Chart(document.getElementById('chart-tour-revenue'),
    vBar(revLbls, revVals, revLbls.map(() => getChartColors().barColor),
      v => v + 'B', v => 'MAD ' + v + 'B'));

  // 7. Seasonality Index (line)
  setH('twrap-season', 220);
  {
    const cc = getChartColors();
    new Chart(document.getElementById('chart-tour-season'), {
      type: 'line',
      data: {
        labels: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
        datasets: [{
          data: [55, 58, 72, 88, 95, 92, 100, 98, 82, 75, 60, 58],
          borderColor: getChartColors().barColor,
          backgroundColor: getChartColors().fillColor,
          fill: false, tension: 0.4,
          pointRadius: 4, pointBackgroundColor: getChartColors().barColor,
          pointBorderColor: '#F9F6F0', pointBorderWidth: 2,
        }],
      },
      options: {
        responsive: true, maintainAspectRatio: false, animation: { duration: 350 },
        layout: { padding: { top: 20 } },
        plugins: {
          legend: { display: false },
          datalabels: {
            anchor: 'top', align: 'top', clip: false,
            color: cc.label, font: { size: 10, weight: '600' },
            formatter: v => v,
          },
          tooltip: {
            backgroundColor: cc.tooltipBg, borderColor: cc.tooltipBdr, borderWidth: 1,
            titleColor: cc.tooltipTtl, bodyColor: cc.tooltipBdy,
            callbacks: { label: ctx => '  Index: ' + ctx.raw },
          },
        },
        scales: {
          x: { ticks: { color: cc.tick, font: { size: 11 } } },
          y: { min: 0, max: 115, ticks: { color: cc.tick, font: { size: 11 } } },
        },
      },
    });
  }

  renderTourismEvents();
  tourismInited = true;
}

// ─── Pipeline screen ──────────────────────────────────────────────

async function initPipeline() {
  if (pipelineInited) {
    if (googlePipelineMap) setTimeout(() => google.maps.event.trigger(googlePipelineMap, 'resize'), 60);
    return;
  }
  pipelineInited = true;

  const res = await fetch('/api/pipeline');
  if (res.status === 403) {
    const err = await res.json().catch(() => ({}));
    if (err.error === 'upgrade_required') {
      pipelineInited = false;
      if (typeof showUpgradeModal === 'function') showUpgradeModal('Pipeline requires Benchmarker', err.message);
      return;
    }
  }
  pipelineData = await res.json();
  buildSearchIndex();

  // Populate filter dropdowns
  const cities = [...new Set(pipelineData.map(p => p.city))].sort();
  const cats   = [...new Set(pipelineData.map(p => p.category))].sort();
  const cityEl = document.getElementById('pipe-city-filter');
  const catEl  = document.getElementById('pipe-cat-filter');
  cities.forEach(c => { const o = document.createElement('option'); o.value = c; o.textContent = c; cityEl.appendChild(o); });
  cats.forEach(c   => { const o = document.createElement('option'); o.value = c; o.textContent = c; catEl.appendChild(o); });

  renderPipelineKPIs();
  renderPipelineCards();
  renderPipelineCharts();
  setTimeout(initPipelineMap, 120);
}

function filteredPipeline() {
  return pipelineData.filter(p =>
    (pipelineState.status === 'all'   || p.status   === pipelineState.status) &&
    (pipelineState.city   === 'all'   || p.city     === pipelineState.city)   &&
    (pipelineState.category === 'all' || p.category === pipelineState.category)
  );
}

function renderPipelineKPIs() {
  const all = pipelineData;
  const totalKeys = all.reduce((s, p) => s + p.keys, 0);
  const totalInv  = all.reduce((s, p) => s + p.investment_mad, 0);
  const by2027    = all.filter(p => p.expected_opening <= 2027).length;

  const setKpi = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.querySelector('.kpi-value').textContent = val;
  };
  setKpi('pkpi-total', all.length);
  setKpi('pkpi-keys',  totalKeys.toLocaleString('en'));
  setKpi('pkpi-inv',   (totalInv / 1e9).toFixed(1) + 'B');
  setKpi('pkpi-2027',  by2027);
}

function initPipelineMap() {
  const container = document.getElementById('pipeline-map-container');
  if (!container || !googleMapsApiReady || googlePipelineMap) return;
  try {
    const isDark = !document.body.classList.contains('light');
    googlePipelineMap = new google.maps.Map(container, {
      ...GMAP_OPTIONS_BASE,
      center: { lat: 31.5, lng: -5.5 },
      zoom:   6,
      styles: isDark ? GMAP_STYLE_DARK : GMAP_STYLE_LIGHT,
    });

    pipelineMarkers = pipelineData.map(p => {
      const color  = p.status === 'Under Construction' ? '#B87860' : '#888888';
      const radius = Math.max(8, Math.sqrt(p.keys) * 0.85);
      const marker = new google.maps.Marker({
        position: { lat: p.lat, lng: p.lng },
        map:      googlePipelineMap,
        icon: {
          path:        google.maps.SymbolPath.CIRCLE,
          scale:       radius,
          fillColor:   color,
          fillOpacity: 0.85,
          strokeColor: color,
          strokeWeight: 1.5,
        },
      });
      marker.addListener('click', () => {
        if (activeInfoWindow) activeInfoWindow.close();
        activeInfoWindow = new google.maps.InfoWindow({ content: pipelinePopupHTML(p) });
        activeInfoWindow.open({ map: googlePipelineMap, anchor: marker });
      });
      return { marker, project: p };
    });
  } catch (e) {
    console.error('Google Maps pipeline init failed:', e);
  }
}

function pipelinePopupHTML(p) {
  const invB = (p.investment_mad / 1e9).toFixed(2);
  const statusPill = p.status === 'Under Construction'
    ? `<span style="background:transparent;color:#B87860;border:1px solid #B87860;border-radius:4px;padding:1px 6px;font-size:10px;font-weight:500;white-space:nowrap;display:inline-block">${p.status}</span>`
    : `<span style="background:transparent;color:#888888;border:1px solid #444444;border-radius:4px;padding:1px 6px;font-size:10px;font-weight:500;white-space:nowrap;display:inline-block">${p.status}</span>`;
  return `<div class="hiq-popup">
    <div class="hiq-popup-name">${fmt.esc(p.name)}</div>
    <div class="hiq-popup-meta">${fmt.esc(p.brand)} · ${fmt.esc(p.category)}</div>
    <div class="hiq-popup-grid">
      <div class="hiq-popup-stat"><div class="hiq-popup-stat-val">${p.keys || 'TBC'}</div><div class="hiq-popup-stat-lbl">Keys</div></div>
      <div class="hiq-popup-stat"><div class="hiq-popup-stat-val">${p.expected_opening}</div><div class="hiq-popup-stat-lbl">Opening</div></div>
      <div class="hiq-popup-stat"><div class="hiq-popup-stat-val">MAD ${invB}B</div><div class="hiq-popup-stat-lbl">Investment</div></div>
      <div class="hiq-popup-stat"><div class="hiq-popup-stat-val">${statusPill}</div><div class="hiq-popup-stat-lbl">Status</div></div>
    </div>
  </div>`;
}

let pipelineChartProj = null;
let pipelineChartCity = null;

function renderPipelineCards() {
  const data = filteredPipeline();
  const grid = document.getElementById('pipe-cards-grid');
  const countEl = document.getElementById('pipe-count');
  if (countEl) countEl.textContent = data.length + ' project' + (data.length !== 1 ? 's' : '');

  if (!data.length) {
    grid.innerHTML = '<p style="color:var(--text-muted);font-size:13px;padding:8px 0">No projects match the selected filters.</p>';
    return;
  }
  grid.innerHTML = data.map(p => {
    const isUC = p.status === 'Under Construction';
    const pill  = isUC ? `<span class="pipe-status-uc">${p.status}</span>` : `<span class="pipe-status-pl">${p.status}</span>`;
    const invM  = Math.round(p.investment_mad / 1e6).toLocaleString('en');
    return `<div class="pipe-card ${isUC ? 'pipe-card-uc' : 'pipe-card-pl'}">
      <div>
        <div class="pipe-card-header-row">
          <div class="pipe-card-name">${fmt.esc(p.name)}</div>
          ${pill}
        </div>
        <div class="pipe-card-location">${fmt.esc(p.city)} · ${fmt.esc(p.category)}</div>
        <div class="pipe-card-brand">${getBrandLogoImg(p.brand, 16)} ${fmt.esc(p.brand)}</div>
      </div>
      <div class="pipe-card-year">${p.expected_opening}</div>
      <div class="pipe-card-metrics">
        <div>
          <div class="pipe-card-metric-val">${p.keys ? p.keys.toLocaleString('en') : 'TBC'}</div>
          <div class="pipe-card-metric-lbl">Keys</div>
        </div>
        <div>
          <div class="pipe-card-metric-val">${invM}</div>
          <div class="pipe-card-metric-lbl">MAD M</div>
        </div>
      </div>
    </div>`;
  }).join('');
}

function renderPipelineTableView() {
  const data = filteredPipeline();
  const tbody = document.getElementById('pipeline-tbody');
  data.sort((a, b) => {
    const av = a[pipelineSort.col], bv = b[pipelineSort.col];
    if (PIPE_STR_COLS.has(pipelineSort.col)) return pipelineSort.dir * String(av).localeCompare(String(bv));
    return pipelineSort.dir * (av - bv);
  });
  if (!data.length) {
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:24px;color:var(--text-muted)">No projects match filters.</td></tr>';
    return;
  }
  tbody.innerHTML = data.map(p => {
    const pill  = p.status === 'Under Construction' ? `<span class="pipe-status-uc">${p.status}</span>` : `<span class="pipe-status-pl">${p.status}</span>`;
    const invM  = Math.round(p.investment_mad / 1e6).toLocaleString('en');
    return `<tr>
      <td style="font-weight:600">${fmt.esc(p.name)}</td>
      <td>${fmt.esc(p.city)}</td>
      <td>${fmt.esc(p.brand)}</td>
      <td class="num-col">${p.expected_opening}</td>
      <td>${pill}</td>
      <td class="num-col">${p.keys.toLocaleString('en')}</td>
      <td class="num-col">${invM}</td>
    </tr>`;
  }).join('');
}

function togglePipelineTable() {
  const wrap = document.getElementById('pipe-table-wrap');
  const btn  = document.getElementById('pipe-table-toggle');
  const open = wrap.classList.toggle('open');
  btn.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M3 9h18M3 15h18M9 3v18M15 3v18" stroke-linecap="round"/></svg> ${open ? 'Hide table view' : 'Show table view'}`;
  if (open) renderPipelineTableView();
}

function renderPipelineCharts() {
  const data = filteredPipeline();

  // Keys by project (horizontal bar, sorted asc so largest at top)
  const sorted = [...data].sort((a, b) => a.keys - b.keys);
  const projLabels = sorted.map(p => p.name);
  const projVals   = sorted.map(p => p.keys);
  const projColors = sorted.map(() => getChartColors().barColor);

  const projWrap = document.getElementById('pwrap-proj');
  if (projWrap) { projWrap.style.minHeight = '0'; projWrap.style.height = Math.max(220, projLabels.length * 36 + 50) + 'px'; }
  if (pipelineChartProj) { pipelineChartProj.destroy(); pipelineChartProj = null; }
  const projCfg = chartConfig(projLabels, projVals, ' keys', projColors, v => v);
  projCfg.options.plugins.tooltip.callbacks.label = ctx => '  ' + ctx.raw + ' keys';
  pipelineChartProj = new Chart(document.getElementById('chart-pipeline-proj'), projCfg);

  // Investment by city (horizontal bar, sorted asc)
  const cityTotals = {};
  data.forEach(p => { cityTotals[p.city] = (cityTotals[p.city] || 0) + p.investment_mad; });
  const cityEntries = Object.entries(cityTotals).sort((a, b) => a[1] - b[1]);
  const cityLabels  = cityEntries.map(e => e[0]);
  const cityVals    = cityEntries.map(e => parseFloat((e[1] / 1e9).toFixed(2)));

  const cityWrap = document.getElementById('pwrap-city');
  if (cityWrap) { cityWrap.style.minHeight = '0'; cityWrap.style.height = Math.max(200, cityLabels.length * 38 + 50) + 'px'; }
  if (pipelineChartCity) { pipelineChartCity.destroy(); pipelineChartCity = null; }
  const cityCfg = chartConfig(cityLabels, cityVals, 'B', cityLabels.map(() => getChartColors().barColor), v => v + 'B');
  cityCfg.options.plugins.tooltip.callbacks.label = ctx => '  MAD ' + ctx.raw + 'B';
  pipelineChartCity = new Chart(document.getElementById('chart-pipeline-city'), cityCfg);
}

function applyPipelineFilter() {
  renderPipelineCards();
  renderPipelineCharts();
  const tableOpen = document.getElementById('pipe-table-wrap').classList.contains('open');
  if (tableOpen) renderPipelineTableView();
  if (googlePipelineMap) {
    pipelineMarkers.forEach(({ marker, project: p }) => {
      const show = (pipelineState.status   === 'all' || p.status   === pipelineState.status) &&
                   (pipelineState.city     === 'all' || p.city     === pipelineState.city)   &&
                   (pipelineState.category === 'all' || p.category === pipelineState.category);
      marker.setMap(show ? googlePipelineMap : null);
    });
  }
}

// Pipeline filter events (event delegation on the screen)
document.getElementById('screen-pipeline').addEventListener('click', e => {
  const btn = e.target.closest('[data-pstatus]');
  if (btn) {
    document.querySelectorAll('[data-pstatus]').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    pipelineState.status = btn.dataset.pstatus;
    applyPipelineFilter();
  }
  const tBtn = e.target.closest('#pipe-table-toggle');
  if (tBtn) togglePipelineTable();
  const th = e.target.closest('th[data-pcol]');
  if (th) {
    const col = th.dataset.pcol;
    pipelineSort.dir = pipelineSort.col === col ? -pipelineSort.dir : 1;
    pipelineSort.col = col;
    document.querySelectorAll('#pipeline-table th').forEach(t => t.classList.remove('sort-asc', 'sort-desc'));
    th.classList.add(pipelineSort.dir === 1 ? 'sort-asc' : 'sort-desc');
    renderPipelineTableView();
  }
});
document.getElementById('pipe-city-filter').addEventListener('change', e => {
  pipelineState.city = e.target.value;
  applyPipelineFilter();
});
document.getElementById('pipe-cat-filter').addEventListener('change', e => {
  pipelineState.category = e.target.value;
  applyPipelineFilter();
});

// ─── Editorial / News screen ──────────────────────────────────────
let newsData    = null;
let newsInited  = false;
let newsCatFilter = 'all';
let newsPage    = 1;
const NEWS_PER_PAGE = 6;

function newsDateFmt(d) {
  if (!d) return '';
  const dt = new Date(d + 'T00:00:00');
  return dt.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
}

function newsCoverUrl(slug, query) {
  return `https://picsum.photos/seed/${encodeURIComponent(slug || query || 'hotel')}/800/450`;
}

function edCatPill(cat, type) {
  const isSponsored = type === 'sponsored' || type === 'partner';
  const label = isSponsored ? 'Partner' : (cat || '');
  const cls   = isSponsored ? 'ed-cat-badge ed-cat-partner' : 'ed-cat-badge';
  return `<span class="${cls}">${fmt.esc(label)}</span>`;
}

async function initNews() {
  if (!newsInited) {
    try {
      const res = await fetch('/api/news');
      newsData   = await res.json();
      newsInited = true;
      buildSearchIndex();
    } catch {
      document.getElementById('ed-grid').innerHTML = '<p class="news-loading">Failed to load articles.</p>';
      return;
    }
  }
  renderEditorialMain();
}

function filteredEditorialArticles() {
  if (!newsData) return [];
  const all = newsData.all || [];
  if (newsCatFilter === 'all') return all.filter(a => !a.featured);
  if (newsCatFilter === 'Sponsored') return all.filter(a => a.type === 'sponsored' || a.type === 'partner');
  return all.filter(a => a.category === newsCatFilter && a.type === 'editorial');
}

function renderEditorialMain() {
  if (!newsData) return;
  newsPage = 1;

  // Hero
  const heroWrap = document.getElementById('ed-hero');
  if (newsCatFilter === 'all' && newsData.featured) {
    const f = newsData.featured;
    heroWrap.innerHTML = `
      <div class="ed-hero-card" data-art-id="${f.id}">
        <div class="ed-hero-body">
          <div class="ed-hero-top">
            <span class="ed-featured-badge">FEATURED</span>
            ${edCatPill(f.category, f.type)}
          </div>
          <h2 class="ed-hero-title">${fmt.esc(f.title || f.headline || '')}</h2>
          <p class="ed-hero-excerpt">${fmt.esc(f.excerpt || f.summary || '')}</p>
          <div class="ed-hero-meta">
            <span>${fmt.esc(f.author || 'Kōdō Editorial')}</span>
            <span class="ed-dot">·</span>
            <span>${newsDateFmt(f.date)}</span>
            <span class="ed-dot">·</span>
            <span>${fmt.esc(f.read_time || '')}</span>
          </div>
          <button class="ed-read-btn" data-art-id="${f.id}">Read article →</button>
        </div>
        <div class="ed-hero-img-wrap">
          <img src="${newsCoverUrl(f.slug, f.cover_image_query)}" alt="${fmt.esc(f.title || '')}"
               class="ed-hero-img" loading="lazy" onerror="this.closest('.ed-hero-img-wrap').style.background='var(--surface-hover)'">
        </div>
      </div>`;
    heroWrap.style.display = '';
  } else {
    heroWrap.innerHTML = '';
    heroWrap.style.display = 'none';
  }

  // Sponsored strip
  const sponsWrap  = document.getElementById('ed-sponsored-wrap');
  const sponsStrip = document.getElementById('ed-sponsored-strip');
  if (newsCatFilter === 'all' && newsData.sponsored && newsData.sponsored.length) {
    sponsStrip.innerHTML = newsData.sponsored.map(s => `
      <div class="ed-spons-card" data-art-id="${s.id}">
        <div class="ed-spons-badge">Partner</div>
        ${s.sponsor_logo_domain
          ? `<img src="https://cdn.brandfetch.io/domain/${s.sponsor_logo_domain}?c=1idptYpdMe9b8BdTIPC"
                  alt="${fmt.esc(s.sponsor_name || '')}" class="ed-spons-logo"
                  onerror="this.style.display='none'">`
          : `<div class="ed-spons-logo-placeholder">${fmt.esc((s.sponsor_name || '?')[0])}</div>`}
        <div class="ed-spons-name">${fmt.esc(s.title || s.headline || '')}</div>
        <div class="ed-spons-by">${fmt.esc(s.sponsor_name || '')}</div>
        <button class="ed-spons-cta" data-art-id="${s.id}">${fmt.esc(s.sponsor_cta_text || 'Learn More →')}</button>
      </div>`).join('');
    sponsWrap.style.display = '';
  } else {
    sponsWrap.style.display = 'none';
  }

  // Article grid
  renderArticleGrid();
}

function renderArticleGrid() {
  const articles = filteredEditorialArticles();
  const grid     = document.getElementById('ed-grid');
  const loadBtn  = document.getElementById('ed-load-more');
  const shown    = articles.slice(0, newsPage * NEWS_PER_PAGE);

  if (!articles.length) {
    grid.innerHTML = '<p class="news-loading">No articles in this category yet.</p>';
    loadBtn.style.display = 'none';
    return;
  }

  grid.innerHTML = shown.map(a => {
    const isSponsored = a.type === 'sponsored' || a.type === 'partner';
    return `<div class="ed-card ${isSponsored ? 'ed-card-sponsored' : ''}" data-art-id="${a.id}">
      <div class="ed-card-img-wrap">
        <img src="${newsCoverUrl(a.slug, a.cover_image_query)}"
             alt="${fmt.esc(a.title || a.headline || '')}" class="ed-card-img" loading="lazy"
             onerror="this.closest('.ed-card-img-wrap').classList.add('ed-img-error')">
      </div>
      <div class="ed-card-body">
        ${edCatPill(a.category, a.type)}
        <div class="ed-card-title">${fmt.esc(a.title || a.headline || '')}</div>
        <div class="ed-card-excerpt">${fmt.esc(a.excerpt || a.summary || '')}</div>
        <div class="ed-card-footer">
          <span>${fmt.esc(a.author || 'Kōdō Editorial')}</span>
          <span class="ed-dot">·</span>
          <span>${newsDateFmt(a.date)}</span>
          <span class="ed-dot">·</span>
          <span>${fmt.esc(a.read_time || '')}</span>
        </div>
      </div>
    </div>`;
  }).join('');

  loadBtn.style.display = shown.length < articles.length ? '' : 'none';
}

function loadMoreArticles() {
  newsPage++;
  renderArticleGrid();
}

async function showArticleDetail(id) {
  const art = (newsData?.all || []).find(a => a.id === id);
  if (!art) return;

  // Increment view counter (fire-and-forget)
  fetch(`/api/news/${id}/view`, { method: 'POST' }).catch(() => {});

  document.getElementById('editorial-view').style.display    = 'none';
  document.getElementById('article-detail-view').style.display = '';

  const isSponsored = art.type === 'sponsored' || art.type === 'partner';

  document.getElementById('art-meta-top').innerHTML =
    `${edCatPill(art.category, art.type)}
     ${isSponsored && art.sponsor_name ? `<span class="ed-spons-by-label">Sponsored by ${fmt.esc(art.sponsor_name)}</span>` : ''}`;

  document.getElementById('art-title').textContent = art.title || art.headline || '';

  document.getElementById('art-byline').innerHTML =
    `<span class="art-author">${fmt.esc(art.author || 'Kōdō Editorial')}</span>
     <span class="ed-dot">·</span>
     <span>${newsDateFmt(art.date)}</span>
     <span class="ed-dot">·</span>
     <span>${fmt.esc(art.read_time || '')}</span>`;

  document.getElementById('art-cover').innerHTML =
    `<img src="${newsCoverUrl(art.slug, art.cover_image_query)}"
          alt="${fmt.esc(art.title || '')}" class="art-cover-img" loading="lazy"
          onerror="this.style.display='none'">`;

  document.getElementById('art-body').innerHTML = art.content || art.body || '';

  const ctaEl = document.getElementById('art-sponsor-cta');
  if (isSponsored && art.sponsor_cta_text) {
    ctaEl.innerHTML = `
      <div class="art-cta-box">
        ${art.sponsor_logo_domain
          ? `<img src="https://cdn.brandfetch.io/domain/${art.sponsor_logo_domain}?c=1idptYpdMe9b8BdTIPC"
                  alt="${fmt.esc(art.sponsor_name || '')}" class="art-cta-logo"
                  onerror="this.style.display='none'">`
          : ''}
        <div class="art-cta-text">Learn more from ${fmt.esc(art.sponsor_name || 'our partner')}</div>
        <a href="${fmt.esc(art.sponsor_cta_url || '#')}" class="art-cta-btn" target="_blank" rel="noopener">
          ${fmt.esc(art.sponsor_cta_text)}
        </a>
      </div>`;
    ctaEl.style.display = '';
  } else {
    ctaEl.style.display = 'none';
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function closeArticleDetail() {
  document.getElementById('article-detail-view').style.display = 'none';
  document.getElementById('editorial-view').style.display      = '';
}

// Category pill filter
document.getElementById('ed-cat-bar').addEventListener('click', e => {
  const btn = e.target.closest('.ed-cat-pill');
  if (!btn) return;
  document.querySelectorAll('.ed-cat-pill').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  newsCatFilter = btn.dataset.cat;
  if (newsInited) renderEditorialMain();
});

// Article clicks — hero, grid, sponsored
document.getElementById('screen-news').addEventListener('click', e => {
  const btn = e.target.closest('[data-art-id]');
  if (!btn) return;
  const id = parseInt(btn.dataset.artId, 10);
  if (!isNaN(id)) showArticleDetail(id);
});

// ─── Sidebar visibility ───────────────────────────────────────────

const SIDEBAR_SCREENS = new Set(['dashboard', 'map']);
function setSidebar(screen) {
  document.querySelector('.app-body').classList.toggle('no-sidebar', !SIDEBAR_SCREENS.has(screen));
}

// ─── Mobile nav ───────────────────────────────────────────────────

function closeMobileNav() {
  const overlay = document.getElementById('mobile-nav-overlay');
  const btn     = document.getElementById('hamburger-btn');
  overlay.classList.remove('open');
  btn.textContent = '☰';
  btn.setAttribute('aria-expanded', 'false');
}

function syncMobileNav(screen) {
  document.querySelectorAll('.mobile-nav-link').forEach(l =>
    l.classList.toggle('active', l.dataset.screen === screen)
  );
}

document.getElementById('hamburger-btn').addEventListener('click', () => {
  const overlay = document.getElementById('mobile-nav-overlay');
  const btn     = document.getElementById('hamburger-btn');
  const isOpen  = overlay.classList.toggle('open');
  btn.textContent = isOpen ? '✕' : '☰';
  btn.setAttribute('aria-expanded', String(isOpen));
});

// ─── Events ───────────────────────────────────────────────────────

// Screen nav
document.querySelectorAll('.nav-link').forEach(link => {
  link.addEventListener('click', e => {
    e.preventDefault();
    const screen = link.dataset.screen;
    closeMobileNav();
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    // Set active on every nav-link (desktop + mobile) matching this screen
    document.querySelectorAll(`.nav-link[data-screen="${screen}"]`).forEach(l => l.classList.add('active'));
    document.getElementById('screen-' + screen).classList.add('active');
    setSidebar(screen);
    syncMobileNav(screen);

    if (screen === 'map') {
      if (!googleMap) {
        initMap();
      } else {
        setTimeout(() => google.maps.event.trigger(googleMap, 'resize'), 60);
        updateMapMarkers();
        panMap();
      }
    }
    if (screen === 'hotels')   renderHotelsTable();
    if (screen === 'brands')   initBrands();
    if (screen === 'tourism')  initTourismCharts();
    if (screen === 'pipeline') initPipeline();
    if (screen === 'news')         initNews();
    if (screen === 'benchmarking') {
      initBenchmarking().then(() => {
        if (benchmarkInited && benchmarkData) renderBenchAIInsights();
      });
    }
    if (screen === 'reports') initReports();
  });
});

// Logo click → navigate to Dashboard
document.getElementById('navbar-logo').addEventListener('click', () => {
  document.querySelector('.nav-link[data-screen="dashboard"]').click();
});

// City filter (sidebar)
document.getElementById('city-filter').addEventListener('click', e => {
  const item = e.target.closest('.sidebar-item');
  if (!item) return;
  document.querySelectorAll('#city-filter .sidebar-item').forEach(el => el.classList.remove('active'));
  item.classList.add('active');
  state.city = item.dataset.city;
  render();
});

// Map segment filter buttons
document.getElementById('map-seg-bar').addEventListener('click', e => {
  const btn = e.target.closest('.seg-btn');
  if (!btn) return;
  document.querySelectorAll('#map-seg-bar .seg-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  state.mapSeg = btn.dataset.mapSeg;
  updateMapMarkers();
});

// Sidebar segment filter (mirrors map seg, visual only on dashboard)
document.getElementById('segment-sidebar').addEventListener('click', e => {
  const item = e.target.closest('.sidebar-item');
  if (!item) return;
  document.querySelectorAll('#segment-sidebar .sidebar-item').forEach(el => el.classList.remove('active'));
  item.classList.add('active');
  // Also sync map segment filter
  state.mapSeg = item.dataset.seg;
  document.querySelectorAll('#map-seg-bar .seg-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.mapSeg === state.mapSeg);
  });
  if (googleMap) updateMapMarkers();
});

// Hotels: search input + clear button
document.getElementById('hotels-search').addEventListener('input', e => {
  hotelsState.query = e.target.value;
  const clearBtn = document.getElementById('hotels-search-clear');
  if (clearBtn) clearBtn.classList.toggle('visible', !!e.target.value);
  renderHotelsTable();
});
document.getElementById('hotels-search-clear').addEventListener('click', () => {
  hotelsState.query = '';
  document.getElementById('hotels-search').value = '';
  document.getElementById('hotels-search-clear').classList.remove('visible');
  renderHotelsTable();
});

// Hotels: sort select
document.getElementById('hotels-sort-select').addEventListener('change', e => {
  const val = e.target.value;
  hotelsState.col = val;
  hotelsState.dir = STRING_COLS.has(val) ? 1 : -1;
  renderHotelsTable();
});

// Hotels: owner select
document.getElementById('hotels-owner-select').addEventListener('change', e => {
  hotelsState.owner = e.target.value;
  renderHotelsTable();
});

// Hotels: active filter chip removal
document.getElementById('hotels-active-filters').addEventListener('click', e => {
  const btn = e.target.closest('.filter-chip-remove');
  if (!btn) return;
  const chip = btn.closest('.filter-chip');
  if (!chip) return;
  const type = chip.dataset.ftype;
  if (type === 'city') {
    hotelsState.city = 'all';
    document.querySelectorAll('#hotels-city-pills .pill').forEach(p =>
      p.classList.toggle('active', p.dataset.hcity === 'all'));
  } else if (type === 'seg') {
    hotelsState.seg = 'all';
    document.querySelectorAll('#hotels-seg-pills .pill').forEach(p =>
      p.classList.toggle('active', p.dataset.hseg === 'all'));
  } else if (type === 'owner') {
    hotelsState.owner = 'all';
    document.getElementById('hotels-owner-select').value = 'all';
  } else if (type === 'query') {
    hotelsState.query = '';
    document.getElementById('hotels-search').value = '';
    document.getElementById('hotels-search-clear').classList.remove('visible');
  }
  renderHotelsTable();
});

// Hotels: clear all filters
document.getElementById('hotels-clear-all').addEventListener('click', clearAllHotelsFilters);

// Hotels: city pills
document.getElementById('hotels-city-pills').addEventListener('click', e => {
  const pill = e.target.closest('.pill');
  if (!pill) return;
  document.querySelectorAll('#hotels-city-pills .pill').forEach(p => p.classList.remove('active'));
  pill.classList.add('active');
  hotelsState.city = pill.dataset.hcity;
  renderHotelsTable();
});

// Tourism: events city filter
document.getElementById('events-city-filter').addEventListener('click', e => {
  const pill = e.target.closest('.events-filter-pill');
  if (!pill) return;
  eventsFilter = pill.dataset.city;
  document.querySelectorAll('#events-city-filter .events-filter-pill').forEach(p => p.classList.remove('active'));
  pill.classList.add('active');
  renderTourismEvents();
});

// Hotels: segment pills
document.getElementById('hotels-seg-pills').addEventListener('click', e => {
  const pill = e.target.closest('.pill');
  if (!pill) return;
  document.querySelectorAll('#hotels-seg-pills .pill').forEach(p => p.classList.remove('active'));
  pill.classList.add('active');
  hotelsState.seg = pill.dataset.hseg;
  renderHotelsTable();
});

// Hotels: column sort (also syncs sort select)
document.getElementById('hotels-table').addEventListener('click', e => {
  const th = e.target.closest('.sortable-col');
  if (!th) return;
  const col = th.dataset.col;
  if (col === hotelsState.col) {
    hotelsState.dir *= -1;
  } else {
    hotelsState.col = col;
    hotelsState.dir = STRING_COLS.has(col) ? 1 : -1;
  }
  renderHotelsTable();
});

// Brand table — click brand group name → brand detail
document.querySelector('#brand-table tbody').addEventListener('click', e => {
  const cell = e.target.closest('.brand-link');
  if (!cell) return;
  showBrandDetail(cell.dataset.brand);
});

// Brand detail — back button (dashboard or brands depending on origin)
document.getElementById('brand-back-btn').addEventListener('click', () => {
  const prev = brandDetailPrevScreen || 'dashboard';
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-link').forEach(l =>
    l.classList.toggle('active', l.dataset.screen === prev)
  );
  const prevEl = document.getElementById('screen-' + prev);
  if (prevEl) prevEl.classList.add('active');
  setSidebar(prev);
  syncMobileNav(prev);
});

// Hotel detail — back button
document.getElementById('hotel-back-btn').addEventListener('click', () => {
  const prev = hotelDetailPrevScreen;
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-link').forEach(l =>
    l.classList.toggle('active', l.dataset.screen === prev)
  );
  const prevScreen = document.getElementById('screen-' + prev);
  if (prevScreen) prevScreen.classList.add('active');
  setSidebar(prev);
  syncMobileNav(prev);
  if (prev === 'map') {
    if (!googleMap) initMap();
    else setTimeout(() => google.maps.event.trigger(googleMap, 'resize'), 60);
  }
});

// Brand detail — hotel table column sort
document.getElementById('brand-hotels-table').addEventListener('click', e => {
  const th = e.target.closest('.sortable-col[data-bcol]');
  if (!th) return;
  const col = th.dataset.bcol;
  if (col === brandState.col) {
    brandState.dir *= -1;
  } else {
    brandState.col = col;
    brandState.dir = BRAND_STR_COLS.has(col) ? 1 : -1;
  }
  renderBrandHotelsTable();
});

// ─── Brands screen events ─────────────────────────────────────────

// Card clicks + comparison table brand clicks → brand detail
document.getElementById('brands-cards-grid').addEventListener('click', e => {
  const card = e.target.closest('[data-brand-group]');
  if (!card) return;
  const bg = card.dataset.brandGroup;
  if (bg) showBrandDetail(bg, 'brands');
});

document.getElementById('brands-comp-tbody').addEventListener('click', e => {
  const row = e.target.closest('[data-brand-group]');
  if (!row) return;
  const bg = row.dataset.brandGroup;
  if (bg) showBrandDetail(bg, 'brands');
});

// Comparison table column sort
document.getElementById('brands-comp-table').addEventListener('click', e => {
  const th = e.target.closest('.sortable-col[data-bccol]');
  if (!th) return;
  const col = th.dataset.bccol;
  if (col === brandsCompSort.col) {
    brandsCompSort.dir *= -1;
  } else {
    brandsCompSort.col = col;
    brandsCompSort.dir = BRANDS_COMP_STR.has(col) ? 1 : -1;
  }
  if (brandsInited) renderBrandsCompTable();
});

// Segment filter pills
document.getElementById('brands-seg-pills').addEventListener('click', e => {
  const btn = e.target.closest('.seg-btn');
  if (!btn) return;
  document.querySelectorAll('#brands-seg-pills .seg-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  brandsFilter.segment = btn.dataset.bseg;
  if (brandsInited) renderBrandsCards();
});

// Search input
document.getElementById('brands-search').addEventListener('input', e => {
  brandsFilter.search = e.target.value;
  if (brandsInited) renderBrandsCards();
});

// Sort select
document.getElementById('brands-sort').addEventListener('change', e => {
  brandsFilter.sort = e.target.value;
  if (brandsInited) renderBrandsCards();
});

// ─── AI Chat ──────────────────────────────────────────────────────

const chatHistory = [];   // { role: 'user' | 'assistant', content: string }
let chatBusy = false;

const chatThread  = document.getElementById('chat-thread');
const chatWelcome = document.getElementById('chat-welcome');
const chatTyping  = document.getElementById('chat-typing');
const chatInput   = document.getElementById('chat-input');
const chatSend    = document.getElementById('chat-send');

function mdRender(text) {
  if (typeof marked === 'undefined' || typeof DOMPurify === 'undefined') return fmt.esc(text);
  return DOMPurify.sanitize(marked.parse(text));
}

function appendMessage(role, content) {
  // Hide welcome state on first message
  if (chatWelcome) chatWelcome.style.display = 'none';

  const wrap = document.createElement('div');
  wrap.className = `chat-msg chat-msg-${role}`;

  if (role === 'assistant' || role === 'error') {
    const label = document.createElement('div');
    label.className = 'msg-label';
    label.textContent = 'Kōdō Analyst';
    wrap.appendChild(label);
  }

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';

  if (role === 'user') {
    bubble.textContent = content;
  } else if (role === 'error') {
    wrap.classList.add('chat-msg-error');
    bubble.innerHTML = `<strong>Error:</strong> ${fmt.esc(content)}`;
  } else {
    bubble.innerHTML = mdRender(content);
  }

  wrap.appendChild(bubble);
  chatThread.appendChild(wrap);
  chatThread.scrollTop = chatThread.scrollHeight;
}

function setLoading(on) {
  chatBusy = on;
  chatSend.disabled = on;
  chatInput.disabled = on;
  chatTyping.style.display = on ? 'flex' : 'none';
  if (on) chatThread.scrollTop = chatThread.scrollHeight;
}

async function sendChat(text) {
  text = text.trim();
  if (!text || chatBusy) return;

  chatInput.value = '';
  chatHistory.push({ role: 'user', content: text });
  appendMessage('user', text);
  setLoading(true);

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: chatHistory }),
    });
    const data = await res.json();

    if (res.status === 403 && data.error === 'upgrade_required') {
      if (typeof showUpgradeModal === 'function') showUpgradeModal('AI Analyst limit reached', data.message);
    } else if (data.error) {
      appendMessage('error', data.error);
    } else {
      chatHistory.push({ role: 'assistant', content: data.response });
      appendMessage('assistant', data.response);
    }
  } catch (err) {
    appendMessage('error', 'Network error — could not reach the server.');
  } finally {
    setLoading(false);
    chatInput.focus();
  }
}

// Send on button click
chatSend.addEventListener('click', () => sendChat(chatInput.value));

// Send on Enter (Shift+Enter = newline not applicable here since it's an input)
chatInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendChat(chatInput.value);
  }
});

// Starter chips
document.getElementById('chat-chips').addEventListener('click', e => {
  const chip = e.target.closest('.chat-chip');
  if (!chip) return;
  sendChat(chip.dataset.q);
});

// ─── Dynamic filters ──────────────────────────────────────────────

function buildCityFilter() {
  const cities = [...new Set(hotels.map(h => h.city))].sort();
  const list = document.getElementById('city-filter');
  list.querySelectorAll('[data-city]:not([data-city="all"])').forEach(el => el.remove());
  cities.forEach(city => {
    const li = document.createElement('li');
    li.className = 'sidebar-item';
    li.dataset.city = city;
    li.textContent = city;
    list.appendChild(li);
  });
}

function buildCityPills() {
  const all    = hotels || [];
  const cities = [...new Set(all.map(h => h.city))].sort();
  const bar    = document.getElementById('hotels-city-pills');
  bar.querySelectorAll('[data-hcity]:not([data-hcity="all"])').forEach(el => el.remove());
  bar.querySelector('[data-hcity="all"]').textContent = `All (${all.length})`;
  cities.forEach(city => {
    const count = all.filter(h => h.city === city).length;
    const btn = document.createElement('button');
    btn.className = 'pill';
    btn.dataset.hcity = city;
    btn.textContent = `${city} (${count})`;
    bar.appendChild(btn);
  });
}

function buildSegPills() {
  const all = hotels || [];
  const bar = document.getElementById('hotels-seg-pills');
  bar.querySelector('[data-hseg="all"]').textContent = `All Segments (${all.length})`;
  ['Ultra Luxury','Luxury','Upper Upscale','Upscale','Midscale'].forEach(seg => {
    const btn = bar.querySelector(`[data-hseg="${seg}"]`);
    if (!btn) return;
    const count = all.filter(h => h.category === seg).length;
    btn.textContent = `${seg} (${count})`;
  });
}

function buildMobileCityPills() {
  const cities = [...new Set(hotels.map(h => h.city))].sort();
  const bar = document.getElementById('mobile-city-pills');
  bar.querySelectorAll('[data-mcity]:not([data-mcity="all"])').forEach(el => el.remove());
  cities.forEach(city => {
    const btn = document.createElement('button');
    btn.className = 'pill';
    btn.dataset.mcity = city;
    btn.textContent = city;
    bar.appendChild(btn);
  });
}

// Mobile city filter
document.getElementById('mobile-city-pills').addEventListener('click', e => {
  const btn = e.target.closest('[data-mcity]');
  if (!btn) return;
  document.querySelectorAll('#mobile-city-pills .pill').forEach(p => p.classList.remove('active'));
  btn.classList.add('active');
  // Sync sidebar
  state.city = btn.dataset.mcity;
  document.querySelectorAll('#city-filter .sidebar-item').forEach(el =>
    el.classList.toggle('active', el.dataset.city === state.city)
  );
  render();
});

// Mobile segment filter
document.getElementById('mobile-seg-pills').addEventListener('click', e => {
  const btn = e.target.closest('[data-mseg]');
  if (!btn) return;
  document.querySelectorAll('#mobile-seg-pills .pill').forEach(p => p.classList.remove('active'));
  btn.classList.add('active');
  state.mapSeg = btn.dataset.mseg;
  document.querySelectorAll('#segment-sidebar .sidebar-item').forEach(el =>
    el.classList.toggle('active', el.dataset.seg === state.mapSeg)
  );
  document.querySelectorAll('#map-seg-bar .seg-btn').forEach(b =>
    b.classList.toggle('active', b.dataset.mapSeg === state.mapSeg)
  );
  if (googleMap) updateMapMarkers();
});

// ─── Benchmarking screen ──────────────────────────────────────────

// Segment adjacency for comp set filtering (ordered most-to-least luxury)
const BENCH_SEGMENTS = ['Ultra Luxury', 'Luxury', 'Upper Upscale', 'Upscale', 'Midscale', 'Economy'];
function benchAllowedSegments(seg) {
  const idx = BENCH_SEGMENTS.indexOf(seg);
  const allowed = new Set([seg]);
  if (idx > 0) allowed.add(BENCH_SEGMENTS[idx - 1]);
  if (idx < BENCH_SEGMENTS.length - 1) allowed.add(BENCH_SEGMENTS[idx + 1]);
  return allowed;
}

const BENCH_MAX_COMP = 8;
const BENCH_MIN_COMP = 3;

let benchmarkInited = false;
let benchmarkData   = null;
let benchTrendRevpar = null;
let benchTrendOcc    = null;
let benchDOWChart    = null;

const benchState = {
  myHotelId:  'demo_1',
  compSet:    new Set(['demo_2', 'demo_3', 'demo_4']),
  dateRange:  30,
  adrCalYear: 2026, adrCalMonth: 5, adrCalView: 'mine',
  occCalYear: 2026, occCalMonth: 5, occCalView: 'mine',
};

async function initBenchmarking() {
  if (benchmarkInited) return;
  benchmarkInited = true;
  const res = await fetch('/api/benchmarking');
  if (res.status === 403) {
    const err = await res.json().catch(() => ({}));
    if (err.error === 'upgrade_required') {
      benchmarkInited = false;
      if (typeof showUpgradeModal === 'function') showUpgradeModal('Benchmarking requires Benchmarker', err.message);
      return;
    }
  }
  benchmarkData = await res.json();
  renderBenchPropertySelector();
  renderBenchCompSetBuilder();
  renderBenchAll();
  updateBenchFreshness();
}

async function updateBenchFreshness() {
  const freshnessEl = document.getElementById('bench-freshness-text');
  const modeEl      = document.getElementById('bench-mode-badge');
  if (!freshnessEl) return;
  try {
    const [scraperRes, occRes] = await Promise.all([
      fetch('/api/scraper/status').then(r => r.ok ? r.json() : null).catch(() => null),
      fetch('/api/occupancy/status').then(r => r.ok ? r.json() : null).catch(() => null),
    ]);
    const hasLive = scraperRes && (scraperRes.hotels_with_live > 0 || scraperRes.done_today > 0);
    const hasOcc  = occRes && occRes.has_data;
    if (hasLive || hasOcc) {
      const lastScrape = scraperRes?.last_run?.slice(0, 10) || '—';
      const modelRun   = occRes?.model_run_date || '—';
      freshnessEl.textContent = `Data as of ${lastScrape} · Occupancy model run ${modelRun}`;
      if (modeEl) { modeEl.textContent = 'Live data available'; modeEl.style.background = 'rgba(45,107,58,0.15)'; modeEl.style.color = 'var(--green)'; }
    } else {
      freshnessEl.textContent = 'Demo mode — sample Marrakech luxury data';
    }
  } catch (e) {
    freshnessEl.textContent = 'Demo mode — sample Marrakech luxury data';
  }
}

// ── Selectors ────────────────────────────────────────────────────

function renderBenchPropertySelector() {
  const sel = document.getElementById('bench-my-hotel');
  sel.innerHTML = benchmarkData.hotels.map(h =>
    `<option value="${h.id}"${h.id === benchState.myHotelId ? ' selected' : ''}>${fmt.esc(h.name)}</option>`
  ).join('');
  updateBenchPropInfo();
  sel.addEventListener('change', () => {
    benchState.myHotelId = sel.value;
    updateBenchPropInfo();
    renderBenchCompSetBuilder();
    renderBenchAll();
  });
}

function updateBenchPropInfo() {
  const h = benchmarkData.hotels.find(x => x.id === benchState.myHotelId);
  if (!h) return;
  document.getElementById('bench-prop-info').innerHTML =
    `<div class="bench-prop-name">${fmt.esc(h.name)}</div>
     <div class="bench-prop-meta">${fmt.esc(h.city)} · ${fmt.esc(h.category)} · ${h.keys} keys</div>`;
}

function renderBenchCompSetBuilder() {
  const container = document.getElementById('bench-comp-checks');
  const myHotel = benchmarkData.hotels.find(x => x.id === benchState.myHotelId);

  // Always remove own property from comp set
  benchState.compSet.delete(benchState.myHotelId);

  // Eligible: same city + same/adjacent segment, not own property
  const allowedSegs = myHotel ? benchAllowedSegments(myHotel.category) : new Set();
  const eligible = benchmarkData.hotels.filter(h =>
    h.id !== benchState.myHotelId &&
    (!myHotel || h.city === myHotel.city) &&
    (!myHotel || allowedSegs.has(h.category))
  );

  // Remove previously selected hotels that are no longer eligible
  benchState.compSet.forEach(id => {
    if (!eligible.find(h => h.id === id)) benchState.compSet.delete(id);
  });

  if (!eligible.length) {
    container.innerHTML = '<p style="font-size:11px;color:var(--text-muted);padding:4px 0">No comparable hotels in this city and segment.</p>';
  } else {
    container.innerHTML = eligible.map(h => {
      const checked = benchState.compSet.has(h.id);
      const maxReached = benchState.compSet.size >= BENCH_MAX_COMP && !checked;
      return `<label class="bench-comp-check-label${checked ? ' active' : ''}${maxReached ? ' bench-comp-check-disabled' : ''}">
        <input type="checkbox" class="bench-comp-cb" value="${h.id}"${checked ? ' checked' : ''}${maxReached ? ' disabled' : ''}>
        ${fmt.esc(h.name)}<span class="bench-comp-keys">${h.keys} keys</span>
      </label>`;
    }).join('');

    container.querySelectorAll('.bench-comp-cb').forEach(cb => {
      cb.addEventListener('change', () => {
        if (cb.checked) {
          if (benchState.compSet.size >= BENCH_MAX_COMP) { cb.checked = false; return; }
          benchState.compSet.add(cb.value);
        } else {
          benchState.compSet.delete(cb.value);
        }
        cb.closest('.bench-comp-check-label').classList.toggle('active', cb.checked);
        // Refresh disabled state on other checkboxes after max changes
        container.querySelectorAll('.bench-comp-cb').forEach(other => {
          const otherChecked = benchState.compSet.has(other.value);
          const shouldDisable = benchState.compSet.size >= BENCH_MAX_COMP && !otherChecked;
          other.disabled = shouldDisable;
          other.closest('.bench-comp-check-label').classList.toggle('bench-comp-check-disabled', shouldDisable);
        });
        updateBenchCompCounter();
        renderCompPills();
        renderBenchAll();
      });
    });
  }

  updateBenchCompCounter();
  renderCompPills();
}

function updateBenchCompCounter() {
  const n = benchState.compSet.size;
  const valid = isCompSetValid();
  const counterEl = document.getElementById('bench-comp-counter');
  const msgEl     = document.getElementById('bench-comp-min-msg');
  if (counterEl) {
    counterEl.textContent = `${n} hotel${n !== 1 ? 's' : ''} selected — minimum ${BENCH_MIN_COMP} required`;
    counterEl.classList.toggle('bench-comp-counter--warn', !valid);
    counterEl.classList.toggle('bench-comp-counter--ok',    valid);
  }
  if (msgEl) msgEl.style.display = valid ? 'none' : 'block';
  // Update comp toggle buttons on both calendars
  ['adr','occ'].forEach(calType => {
    document.querySelectorAll(`[data-ctype="${calType}"][data-cview="comp"]`).forEach(btn => {
      btn.disabled = !valid;
      btn.title    = valid ? '' : 'Add at least 3 hotels to view comp set data';
      btn.style.opacity = valid ? '' : '0.4';
      btn.style.cursor  = valid ? '' : 'not-allowed';
    });
  });
}

function renderCompPills() {
  const c = document.getElementById('bench-comp-pills');
  c.innerHTML = [...benchState.compSet].map(id => {
    const h = benchmarkData.hotels.find(x => x.id === id);
    if (!h) return '';
    return `<span class="bench-comp-pill">${fmt.esc(h.name)}
      <button class="bench-comp-pill-rm" data-compid="${h.id}">×</button></span>`;
  }).join('');
  c.querySelectorAll('.bench-comp-pill-rm').forEach(btn => {
    btn.addEventListener('click', () => {
      benchState.compSet.delete(btn.dataset.compid);
      const cb = document.querySelector(`.bench-comp-cb[value="${btn.dataset.compid}"]`);
      if (cb) { cb.checked = false; cb.closest('.bench-comp-check-label').classList.remove('active'); }
      updateBenchCompCounter();
      renderCompPills();
      renderBenchAll();
    });
  });
}

// ── Date range ───────────────────────────────────────────────────

function getBenchDateRange() {
  const end = new Date('2026-06-01');
  const start = new Date(end);
  if (benchState.dateRange === 7)        start.setDate(end.getDate() - 6);
  else if (benchState.dateRange === 30)  start.setDate(end.getDate() - 29);
  else if (benchState.dateRange === 90)  start.setDate(end.getDate() - 89);
  else if (benchState.dateRange === 'ytd') { start.setFullYear(end.getFullYear()); start.setMonth(0); start.setDate(1); }
  return [start, end];
}

function dateInRange(dateStr, start, end) {
  const d = new Date(dateStr + 'T00:00:00');
  return d >= start && d <= end;
}

// ── Data helpers ─────────────────────────────────────────────────

function getMyDaily() {
  const [s, e] = getBenchDateRange();
  return benchmarkData.daily.filter(d =>
    d.hotel_id === benchState.myHotelId && dateInRange(d.date, s, e)
  ).sort((a, b) => a.date.localeCompare(b.date));
}

function isCompSetValid() {
  return benchState.compSet.size >= BENCH_MIN_COMP;
}

function benchCompPlaceholder() {
  return `<div style="display:flex;align-items:center;justify-content:center;padding:32px 16px;color:var(--text-muted);font-family:'Plus Jakarta Sans',sans-serif;font-size:11px;text-align:center;">
    ⚠ Add at least ${BENCH_MIN_COMP} hotels to view comp set data
  </div>`;
}

function getCompDaily() {
  if (!isCompSetValid()) return [];  // privacy: minimum 3 required
  const [s, e] = getBenchDateRange();
  const byDate = {};
  benchmarkData.daily.forEach(d => {
    if (!benchState.compSet.has(d.hotel_id)) return;
    if (!dateInRange(d.date, s, e)) return;
    if (!byDate[d.date]) byDate[d.date] = [];
    byDate[d.date].push(d);
  });
  return Object.entries(byDate).map(([date, recs]) => ({
    date,
    occupancy:     recs.reduce((s, r) => s + r.occupancy, 0) / recs.length,
    adr:           recs.reduce((s, r) => s + r.adr, 0) / recs.length,
    revpar:        recs.reduce((s, r) => s + r.revpar, 0) / recs.length,
    rooms_revenue: recs.reduce((s, r) => s + r.rooms_revenue, 0) / recs.length,
  })).sort((a, b) => a.date.localeCompare(b.date));
}

function aggDaily(records) {
  if (!records.length) return { occupancy: 0, adr: 0, revpar: 0, rooms_revenue: 0 };
  const n = records.length;
  return {
    occupancy:     records.reduce((s, r) => s + r.occupancy, 0) / n,
    adr:           records.reduce((s, r) => s + r.adr, 0) / n,
    revpar:        records.reduce((s, r) => s + r.revpar, 0) / n,
    rooms_revenue: records.reduce((s, r) => s + r.rooms_revenue, 0) / n,
  };
}

// ── Master render ─────────────────────────────────────────────────

function renderBenchAll() {
  renderBenchKPIs();
  renderBenchCalendar('adr');
  renderBenchCalendar('occ');
  renderBenchTrends();
  renderBenchDOW();
  renderBenchMonthlyTable();
}

// ── KPI cards ────────────────────────────────────────────────────

function renderBenchKPIs() {
  const my   = aggDaily(getMyDaily());
  const comp = aggDaily(getCompDaily());

  const noComp = benchState.compSet.size < 3;

  function setCard(id, myVal, compVal, myFmt, compFmt) {
    const card = document.getElementById(id);
    card.querySelector('.bench-kpi-mine-val').textContent = myFmt(myVal);
    card.querySelector('.bench-kpi-comp-val').textContent = noComp ? '—' : compFmt(compVal);
    const idx = (!noComp && compVal > 0) ? Math.round(myVal / compVal * 100) : null;
    const idxEl   = card.querySelector('.bench-kpi-index');
    const idxVal  = card.querySelector('.bench-kpi-idx-val');
    idxVal.textContent = idx !== null ? idx : '—';
    idxEl.className = 'bench-kpi-index' + (idx === null ? ' bench-idx-neutral' : idx >= 100 ? ' bench-idx-green' : ' bench-idx-red');
  }

  setCard('bkpi-occ',    my.occupancy,     comp.occupancy,     v => (v*100).toFixed(1)+'%',         v => (v*100).toFixed(1)+'%');
  setCard('bkpi-adr',    my.adr,           comp.adr,           v => 'MAD '+Math.round(v).toLocaleString('en'), v => 'MAD '+Math.round(v).toLocaleString('en'));
  setCard('bkpi-revpar', my.revpar,        comp.revpar,        v => 'MAD '+Math.round(v).toLocaleString('en'), v => 'MAD '+Math.round(v).toLocaleString('en'));
  setCard('bkpi-rev',    my.rooms_revenue, comp.rooms_revenue, v => 'MAD '+Math.round(v).toLocaleString('en'), v => 'MAD '+Math.round(v).toLocaleString('en'));
}

// ── Calendar ──────────────────────────────────────────────────────

function benchCalDataMap(type, year, month) {
  const prefix = `${year}-${String(month).padStart(2,'0')}`;
  const map = {};

  if (type === 'adr') {
    // buildForHotel (mine) or comp average
    const view = benchState.adrCalView;
    buildCalMap(view, prefix, map);
  } else {
    const view = benchState.occCalView;
    buildCalMap(view, prefix, map);
  }
  return map;
}

function buildCalMap(view, prefix, map) {
  if (view === 'mine') {
    benchmarkData.daily.forEach(d => {
      if (d.hotel_id !== benchState.myHotelId) return;
      if (!d.date.startsWith(prefix)) return;
      map[d.date] = { adr: d.adr, occupancy: d.occupancy, revpar: d.revpar };
    });
  } else {
    if (!isCompSetValid()) return;  // privacy: no data below minimum
    const byDate = {};
    benchmarkData.daily.forEach(d => {
      if (!benchState.compSet.has(d.hotel_id)) return;
      if (!d.date.startsWith(prefix)) return;
      if (!byDate[d.date]) byDate[d.date] = [];
      byDate[d.date].push(d);
    });
    Object.entries(byDate).forEach(([date, recs]) => {
      map[date] = {
        adr:       recs.reduce((s, r) => s + r.adr, 0) / recs.length,
        occupancy: recs.reduce((s, r) => s + r.occupancy, 0) / recs.length,
        revpar:    recs.reduce((s, r) => s + r.revpar, 0) / recs.length,
      };
    });
  }
}

function adrCellStyle(adr, isCompSet = false) {
  const dark = !document.body.classList.contains('light');
  if (isCompSet) {
    if (dark) {
      if (adr >= 6000) return {bg:'#2A4A6B', col:'#FFFFFF',  fw:'600', border:''};
      if (adr >= 4000) return {bg:'#1A2E42', col:'#8AB0D0',  fw:'500', border:''};
      return {bg:'#0A1520', col:'#6A8AAA', fw:'', border:'1px solid #2A4A6B'};
    } else {
      if (adr >= 6000) return {bg:'#D0E4F5', col:'#1A4A7A', fw:'600', border:'1px solid #5A90C8'};
      if (adr >= 4000) return {bg:'#E8F2FC', col:'#2A6AAA', fw:'',    border:'1px solid #8AB8E0'};
      return {bg:'#F5F9FF', col:'#5A8AB0', fw:'', border:'1px solid #C0D8F0'};
    }
  }
  if (dark) {
    if (adr >= 6000) return {bg:'#B87860', col:'#0A0A0A', fw:'600', border:''};
    if (adr >= 4000) return {bg:'#6B4838', col:'#F0EDE6', fw:'500', border:''};
    return {bg:'#1C1C1A', col:'#888888', fw:'', border:'1px solid #B87860'};
  } else {
    if (adr >= 6000) return {bg:'#F5EDE8', col:'#6B3828', fw:'600', border:'1px solid #A06848'};
    if (adr >= 4000) return {bg:'#FAF2EE', col:'#A06848', fw:'',    border:'1px solid #C88870'};
    return {bg:'#FFFFFF', col:'#8A8A8A', fw:'', border:'1px solid #ECECEC'};
  }
}

function occCellStyle(occ, isCompSet = false) {
  const dark = !document.body.classList.contains('light');
  const p = occ * 100;
  if (isCompSet) {
    if (dark) {
      if (p >= 80) return {bg:'#1A4A3A', col:'#FFFFFF',  fw:'600', border:''};
      if (p >= 60) return {bg:'#0F2E24', col:'#5A9A82',  fw:'500', border:''};
      return {bg:'#051510', col:'#3A7A62', fw:'', border:'1px solid #1A4A3A'};
    } else {
      if (p >= 80) return {bg:'#D0EDE5', col:'#0A4A32', fw:'600', border:'1px solid #3A9A7A'};
      if (p >= 60) return {bg:'#E5F5EF', col:'#1A6A4A', fw:'',    border:'1px solid #7ABDA8'};
      return {bg:'#F0FAF6', col:'#3A8A68', fw:'', border:'1px solid #B0D8C8'};
    }
  }
  if (dark) {
    if (p >= 80) return {bg:'#C8922A', col:'#0A0A0A', fw:'600', border:''};
    if (p >= 60) return {bg:'#7A5818', col:'#F0EDE6', fw:'500', border:''};
    return {bg:'#1C1C1A', col:'#888888', fw:'', border:'1px solid #7A5818'};
  } else {
    if (p >= 80) return {bg:'#FDF3E0', col:'#6B4A10', fw:'600', border:'1px solid #C8922A'};
    if (p >= 60) return {bg:'#FEF8EE', col:'#8B6820', fw:'',    border:'1px solid #E0B860'};
    return {bg:'#FFFFFF', col:'#8A8A8A', fw:'', border:'1px solid #ECECEC'};
  }
}

function renderBenchCalendar(calType) {
  const yr  = calType === 'adr' ? benchState.adrCalYear  : benchState.occCalYear;
  const mo  = calType === 'adr' ? benchState.adrCalMonth : benchState.occCalMonth;
  let   view = calType === 'adr' ? benchState.adrCalView : benchState.occCalView;

  const valid = isCompSetValid();

  // If comp view is active but comp set is invalid, force back to mine
  if (!valid && view === 'comp') {
    view = 'mine';
    if (calType === 'adr') benchState.adrCalView = 'mine';
    else benchState.occCalView = 'mine';
  }

  const MON_NAMES = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  document.getElementById(`bench-${calType}-month-label`).textContent = `${MON_NAMES[mo-1]} ${yr}`;

  // Update toggle button active state; disable comp button when invalid
  document.querySelectorAll(`[data-ctype="${calType}"]`).forEach(btn => {
    btn.classList.toggle('active', btn.dataset.cview === view);
    if (btn.dataset.cview === 'comp') {
      btn.disabled = !valid;
      btn.title = valid ? '' : 'Add at least 3 hotels to view comp set data';
      btn.style.opacity = valid ? '' : '0.4';
      btn.style.cursor  = valid ? '' : 'not-allowed';
    }
  });

  const dataMap = benchCalDataMap(calType, yr, mo);
  const firstDow = (new Date(yr, mo - 1, 1).getDay() + 6) % 7; // Mon=0
  const totalDays = new Date(yr, mo, 0).getDate();

  let html = '<div class="bench-cal-dow-row">';
  ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'].forEach(d => { html += `<div class="bench-cal-dow">${d}</div>`; });
  html += '</div><div class="bench-cal-days">';
  for (let i = 0; i < firstDow; i++) html += '<div class="bench-cal-day bench-cal-empty"></div>';

  for (let day = 1; day <= totalDays; day++) {
    const dateStr = `${yr}-${String(mo).padStart(2,'0')}-${String(day).padStart(2,'0')}`;
    const isWknd = [0,6].includes((new Date(yr, mo-1, day).getDay()));
    const d = dataMap[dateStr];
    if (d) {
      const isComp = view === 'comp';
      const sty = calType === 'adr' ? adrCellStyle(d.adr, isComp) : occCellStyle(d.occupancy, isComp);
      const dispVal = calType === 'adr'
        ? Math.round(d.adr).toLocaleString('en')
        : (d.occupancy * 100).toFixed(0) + '%';
      const tip = `${dateStr}|${Math.round(d.adr)}|${(d.occupancy*100).toFixed(1)}|${Math.round(d.revpar)}`;
      const dark = !document.body.classList.contains('light');
      const dayNumCol = dark ? '#888888' : '#AAAAAA';
      const styAttr = `background:${sty.bg};color:${sty.col};${sty.fw ? `font-weight:${sty.fw};` : ''}${sty.border ? `border:${sty.border};` : ''}`;
      html += `<div class="bench-cal-day${isWknd ? ' bench-cal-weekend' : ''}"
        style="${styAttr}"
        data-btip="${tip}">
        <span class="bench-cal-daynum" style="color:${dayNumCol};opacity:1">${day}</span>
        <span class="bench-cal-dayval">${dispVal}</span>
      </div>`;
    } else {
      html += `<div class="bench-cal-day bench-cal-nodata${isWknd ? ' bench-cal-weekend' : ''}">
        <span class="bench-cal-daynum">${day}</span>
      </div>`;
    }
  }
  html += '</div>';

  // If comp is requested but invalid, replace entire grid with placeholder
  if (!valid && view === 'comp') {
    html = benchCompPlaceholder();
  }

  document.getElementById(`bench-${calType}-grid`).innerHTML = html;
}

// Tooltip shared between both calendars
const benchTip = document.getElementById('bench-cal-tooltip');

document.addEventListener('mousemove', e => {
  if (benchTip && benchTip.style.display !== 'none') {
    benchTip.style.left = (e.clientX + 14) + 'px';
    benchTip.style.top  = (e.clientY - 10) + 'px';
  }
});

document.getElementById('screen-benchmarking').addEventListener('mouseover', e => {
  const cell = e.target.closest('[data-btip]');
  if (!cell) { benchTip.style.display = 'none'; return; }
  const [dt, adr, occ, rev] = cell.dataset.btip.split('|');
  benchTip.innerHTML = `
    <div class="bct-date">${dt}</div>
    <div class="bct-row"><span>ADR</span><span>MAD ${Number(adr).toLocaleString('en')}</span></div>
    <div class="bct-row"><span>Occupancy</span><span>${occ}%</span></div>
    <div class="bct-row"><span>RevPAR</span><span>MAD ${Number(rev).toLocaleString('en')}</span></div>`;
  benchTip.style.display = 'block';
});
document.getElementById('screen-benchmarking').addEventListener('mouseout', e => {
  if (!e.target.closest('[data-btip]')) benchTip.style.display = 'none';
});

// Calendar nav + view toggle events
document.getElementById('bench-adr-prev').addEventListener('click', () => {
  benchState.adrCalMonth--; if (benchState.adrCalMonth < 1) { benchState.adrCalMonth = 12; benchState.adrCalYear--; }
  renderBenchCalendar('adr');
});
document.getElementById('bench-adr-next').addEventListener('click', () => {
  benchState.adrCalMonth++; if (benchState.adrCalMonth > 12) { benchState.adrCalMonth = 1; benchState.adrCalYear++; }
  renderBenchCalendar('adr');
});
document.getElementById('bench-occ-prev').addEventListener('click', () => {
  benchState.occCalMonth--; if (benchState.occCalMonth < 1) { benchState.occCalMonth = 12; benchState.occCalYear--; }
  renderBenchCalendar('occ');
});
document.getElementById('bench-occ-next').addEventListener('click', () => {
  benchState.occCalMonth++; if (benchState.occCalMonth > 12) { benchState.occCalMonth = 1; benchState.occCalYear++; }
  renderBenchCalendar('occ');
});

document.getElementById('screen-benchmarking').addEventListener('click', e => {
  const btn = e.target.closest('.bench-cal-view-btn');
  if (!btn) return;
  const ctype = btn.dataset.ctype;
  const cview = btn.dataset.cview;
  if (ctype === 'adr') benchState.adrCalView = cview;
  else benchState.occCalView = cview;
  renderBenchCalendar(ctype);
});

// ── Trend charts ──────────────────────────────────────────────────

function renderBenchTrends() {
  const myD   = getMyDaily();
  const compD = getCompDaily();

  const labels = myD.map(d => {
    const dt = new Date(d.date + 'T00:00:00');
    return dt.toLocaleDateString('en-GB', { month: 'short', day: 'numeric' });
  });

  const compByDate = {};
  compD.forEach(d => { compByDate[d.date] = d; });

  const myRevpar  = myD.map(d => Math.round(d.revpar));
  const myOcc     = myD.map(d => parseFloat((d.occupancy * 100).toFixed(1)));
  const cRevpar   = myD.map(d => { const c = compByDate[d.date]; return c ? Math.round(c.revpar) : null; });
  const cOcc      = myD.map(d => { const c = compByDate[d.date]; return c ? parseFloat((c.occupancy * 100).toFixed(1)) : null; });

  const dense = labels.length > 50;

  function mkTrend(myData, compData, suffix) {
    const cc = getChartColors();
    const datasets = [
      { label: 'My Property', data: myData, borderColor: getChartColors().barColor,
        backgroundColor: getChartColors().fillColor, borderWidth: 2, fill: false,
        tension: 0.3, pointRadius: dense ? 0 : 2.5, pointBackgroundColor: getChartColors().barColor },
    ];
    if (isCompSetValid()) {
      datasets.push({ label: 'Comp Set Avg', data: compData, borderColor: '#444444',
        borderWidth: 2, borderDash: [5, 4], fill: false, tension: 0.3, pointRadius: 0 });
    }
    return {
      type: 'line',
      data: { labels, datasets },
      options: {
        responsive: true, maintainAspectRatio: false, animation: { duration: 300 },
        layout: { padding: { top: 14 } },
        plugins: {
          legend: { display: true, labels: { color: cc.tick, font: { size: 11 }, boxWidth: 22, padding: 14 } },
          datalabels: { display: false },
          tooltip: {
            backgroundColor: cc.tooltipBg, borderColor: cc.tooltipBdr, borderWidth: 1,
            titleColor: cc.tooltipTtl, bodyColor: cc.tooltipBdy,
            mode: 'index', intersect: false,
            callbacks: { label: ctx => `  ${ctx.dataset.label}: ${ctx.raw}${suffix}` },
          },
        },
        scales: {
          x: { ticks: { color: cc.tick, font: { size: 10 }, maxTicksLimit: 10, maxRotation: 0 } },
          y: { ticks: { color: cc.tick, font: { size: 11 } } },
        },
      },
    };
  }

  const rWrap = document.getElementById('bench-trend-revpar-wrap');
  rWrap.style.minHeight = '0'; rWrap.style.height = '230px';
  if (benchTrendRevpar) { benchTrendRevpar.destroy(); benchTrendRevpar = null; }
  benchTrendRevpar = new Chart(document.getElementById('bench-trend-revpar'), mkTrend(myRevpar, cRevpar, ' MAD'));

  const oWrap = document.getElementById('bench-trend-occ-wrap');
  oWrap.style.minHeight = '0'; oWrap.style.height = '230px';
  if (benchTrendOcc) { benchTrendOcc.destroy(); benchTrendOcc = null; }
  benchTrendOcc = new Chart(document.getElementById('bench-trend-occ'), mkTrend(myOcc, cOcc, '%'));
}

// ── DOW chart ─────────────────────────────────────────────────────

function renderBenchDOW() {
  const myD   = getMyDaily();
  const compD = getCompDaily();

  const myDOW   = Array(7).fill(null).map(() => []);
  const compDOW = Array(7).fill(null).map(() => []);

  myD.forEach(d => {
    const dow = (new Date(d.date + 'T00:00:00').getDay() + 6) % 7;
    myDOW[dow].push(d.occupancy * 100);
  });
  compD.forEach(d => {
    const dow = (new Date(d.date + 'T00:00:00').getDay() + 6) % 7;
    compDOW[dow].push(d.occupancy * 100);
  });

  const avg = arr => arr.length ? parseFloat((arr.reduce((s,v) => s+v, 0) / arr.length).toFixed(1)) : 0;

  const dWrap = document.getElementById('bench-dow-wrap');
  dWrap.style.minHeight = '0'; dWrap.style.height = '230px';
  if (benchDOWChart) { benchDOWChart.destroy(); benchDOWChart = null; }

  {
    const cc = getChartColors();
    const dowDatasets = [
      { label: 'My Property', data: myDOW.map(avg), backgroundColor: getChartColors().barColor, hoverBackgroundColor: getChartColors().hoverColor, borderRadius: 4, borderSkipped: false },
    ];
    if (isCompSetValid()) {
      dowDatasets.push({ label: 'Comp Set Avg', data: compDOW.map(avg), backgroundColor: 'rgba(68,68,68,0.35)', borderRadius: 4, borderSkipped: false });
    }
    benchDOWChart = new Chart(document.getElementById('bench-dow-chart'), {
      type: 'bar',
      data: {
        labels: ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],
        datasets: dowDatasets,
      },
      options: {
        responsive: true, maintainAspectRatio: false, animation: { duration: 300 },
        layout: { padding: { top: 14 } },
        plugins: {
          legend: { display: false },
          datalabels: { display: false },
          tooltip: {
            backgroundColor: cc.tooltipBg, borderColor: cc.tooltipBdr, borderWidth: 1,
            titleColor: cc.tooltipTtl, bodyColor: cc.tooltipBdy,
            callbacks: { label: ctx => `  ${ctx.dataset.label}: ${ctx.raw}%` },
          },
        },
        scales: {
          x: { ticks: { color: cc.tick, font: { size: 11 } } },
          y: { suggestedMin: 0, suggestedMax: 100, ticks: { color: cc.tick, font: { size: 11 } } },
        },
      },
    });
  }
}

// ── Monthly summary table ─────────────────────────────────────────

function renderBenchMonthlyTable() {
  const months = {};
  benchmarkData.daily.forEach(d => {
    const mk = d.date.substring(0, 7);
    if (!months[mk]) months[mk] = { my: [], compByDate: {} };
    if (d.hotel_id === benchState.myHotelId) {
      months[mk].my.push(d);
    } else if (benchState.compSet.has(d.hotel_id)) {
      if (!months[mk].compByDate[d.date]) months[mk].compByDate[d.date] = [];
      months[mk].compByDate[d.date].push(d);
    }
  });

  const MON_NAMES = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const tbody = document.getElementById('bench-monthly-tbody');
  tbody.innerHTML = Object.keys(months).sort().map(mk => {
    const { my, compByDate } = months[mk];
    const myAgg = aggDaily(my);
    const compDailyAvg = Object.values(compByDate).map(recs => aggDaily(recs));
    const compAgg = aggDaily(compDailyAvg);
    const noComp = benchState.compSet.size < 3 || !compDailyAvg.length;
    const revIdx = (!noComp && compAgg.revpar > 0) ? Math.round(myAgg.revpar / compAgg.revpar * 100) : null;
    const [yr, mo] = mk.split('-');
    const label = `${MON_NAMES[Number(mo)-1]} ${yr}`;
    const idxCls = revIdx === null ? 'bench-idx-neutral' : revIdx >= 100 ? 'bench-idx-green' : 'bench-idx-red';
    return `<tr>
      <td><strong>${label}</strong></td>
      <td>${(myAgg.occupancy*100).toFixed(1)}%</td>
      <td>${noComp ? '—' : (compAgg.occupancy*100).toFixed(1)+'%'}</td>
      <td>${Math.round(myAgg.adr).toLocaleString('en')}</td>
      <td>${noComp ? '—' : Math.round(compAgg.adr).toLocaleString('en')}</td>
      <td>${Math.round(myAgg.revpar).toLocaleString('en')}</td>
      <td>${noComp ? '—' : Math.round(compAgg.revpar).toLocaleString('en')}</td>
      <td><span class="bench-idx-badge ${idxCls}">${revIdx !== null ? revIdx : '—'}</span></td>
    </tr>`;
  }).join('');
}

// ── AI Insights ───────────────────────────────────────────────────

const DOW_NAMES_FULL = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
const DOW_NAMES_SHORT = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];

function renderBenchInsightCards() {
  const box    = document.getElementById('bench-ai-insights');
  const my     = aggDaily(getMyDaily());
  const comp   = aggDaily(getCompDaily());
  const noComp = benchState.compSet.size < 3;
  const myDailyData = getMyDaily();

  // ── Card 1: ADR ──────────────────────────────────────────────
  const adrDiff  = noComp ? 0 : (my.adr - comp.adr) / comp.adr * 100;
  const card1 = {
    icon: '📈',
    headline: noComp ? 'ADR Snapshot' : adrDiff >= 0 ? 'ADR Leadership' : 'ADR Gap',
    body: noComp
      ? `Your ADR stands at MAD ${Math.round(my.adr).toLocaleString('en')}. Select a comp set to benchmark against the market.`
      : adrDiff >= 0
        ? `Your ADR leads the comp set by ${adrDiff.toFixed(1)}% — MAD ${Math.round(my.adr).toLocaleString('en')} vs comp avg MAD ${Math.round(comp.adr).toLocaleString('en')}.`
        : `Your ADR trails the comp set by ${Math.abs(adrDiff).toFixed(1)}% — MAD ${Math.round(my.adr).toLocaleString('en')} vs comp avg MAD ${Math.round(comp.adr).toLocaleString('en')}.`,
    badge: noComp ? `MAD ${Math.round(my.adr).toLocaleString('en')}` : (adrDiff >= 0 ? '+' : '') + adrDiff.toFixed(1) + '% vs comp',
    cls: noComp ? 'bib-amber' : adrDiff >= 2 ? 'bib-green' : adrDiff > -2 ? 'bib-amber' : 'bib-red',
  };

  // ── Card 2: Occupancy ────────────────────────────────────────
  const occDiff = noComp ? 0 : (my.occupancy - comp.occupancy) * 100;
  const card2 = {
    icon: '🏨',
    headline: noComp ? 'Occupancy Snapshot' : occDiff >= 0 ? 'Occupancy Advantage' : 'Occupancy Gap',
    body: noComp
      ? `Running at ${(my.occupancy * 100).toFixed(1)}% occupancy. Add a comp set to see relative performance.`
      : occDiff >= 0
        ? `Occupancy leads comp by ${occDiff.toFixed(1)} pts (${(my.occupancy*100).toFixed(1)}% vs ${(comp.occupancy*100).toFixed(1)}%), indicating stronger demand capture.`
        : `Occupancy trails comp by ${Math.abs(occDiff).toFixed(1)} pts (${(my.occupancy*100).toFixed(1)}% vs ${(comp.occupancy*100).toFixed(1)}%) — review pricing and distribution mix.`,
    badge: noComp ? `${(my.occupancy*100).toFixed(1)}%` : (occDiff >= 0 ? '+' : '') + occDiff.toFixed(1) + ' pts vs comp',
    cls: noComp ? 'bib-amber' : occDiff >= 2 ? 'bib-green' : occDiff > -2 ? 'bib-amber' : 'bib-red',
  };

  // ── Card 3: Best day of week ─────────────────────────────────
  const dowBuckets = Array(7).fill(null).map(() => []);
  myDailyData.forEach(d => {
    const dow = (new Date(d.date + 'T00:00:00').getDay() + 6) % 7;
    dowBuckets[dow].push(d.occupancy * 100);
  });
  const dowAvg     = dowBuckets.map(arr => arr.length ? arr.reduce((s,v)=>s+v,0)/arr.length : 0);
  const validDows  = dowAvg.map((v, i) => ({ v, i })).filter(x => x.v > 0);
  const bestDow    = validDows.reduce((a, b) => b.v > a.v ? b : a, { v: 0, i: 0 });
  const worstDow   = validDows.reduce((a, b) => b.v < a.v ? b : a, { v: 100, i: 0 });
  const spread     = bestDow.v - worstDow.v;
  const isWkndPeak = bestDow.i >= 4;
  const card3 = {
    icon: '📅',
    headline: isWkndPeak ? 'Weekend Strength' : 'Midweek Leader',
    body: `${DOW_NAMES_FULL[bestDow.i]} is your strongest day at ${bestDow.v.toFixed(1)}% vs ${DOW_NAMES_SHORT[worstDow.i]} at ${worstDow.v.toFixed(1)}%. ${spread > 15 ? 'Wide spread — targeted midweek promotions could close the gap.' : 'Consistent demand across the week.'}`,
    badge: `${DOW_NAMES_SHORT[bestDow.i]} peaks at ${bestDow.v.toFixed(0)}%`,
    cls: 'bib-amber',
  };

  // ── Card 4: RevPAR trend ─────────────────────────────────────
  const sorted  = [...myDailyData].sort((a, b) => a.date.localeCompare(b.date));
  const half    = Math.floor(sorted.length / 2);
  const firstH  = sorted.slice(0, half);
  const secondH = sorted.slice(half);
  const rev1    = firstH.length  ? firstH.reduce((s,d)=>s+d.revpar,0)/firstH.length   : 0;
  const rev2    = secondH.length ? secondH.reduce((s,d)=>s+d.revpar,0)/secondH.length  : 0;
  const trendPct = rev1 > 0 ? (rev2 - rev1) / rev1 * 100 : 0;
  const improving = trendPct >= 0;
  const card4 = {
    icon: improving ? '💡' : '⚠️',
    headline: improving ? 'Improving Momentum' : 'Declining Trend',
    body: `RevPAR ${improving ? 'improved' : 'declined'} ${Math.abs(trendPct).toFixed(1)}% from the first to second half of the selected period (MAD ${Math.round(rev1).toLocaleString('en')} → MAD ${Math.round(rev2).toLocaleString('en')}).`,
    badge: (improving ? '+' : '') + trendPct.toFixed(1) + '% vs prior period',
    cls: improving ? 'bib-green' : 'bib-red',
  };

  const cards = [card1, card2, card3, card4];
  box.innerHTML = `
    <div class="bench-insight-grid">
      ${cards.map(c => `
        <div class="bench-insight-card">
          <div class="bench-insight-icon">${c.icon}</div>
          <div class="bench-insight-headline">${fmt.esc(c.headline)}</div>
          <div class="bench-insight-body">${fmt.esc(c.body)}</div>
          <span class="bench-insight-badge ${c.cls}">${fmt.esc(c.badge)}</span>
        </div>`).join('')}
    </div>
    <div id="bench-ai-commentary" class="bench-ai-commentary" style="display:none">
      <div class="bench-ai-commentary-label">✦ AI Commentary</div>
      <div id="bench-ai-commentary-body" class="bench-loading">Generating…</div>
    </div>`;
}

async function fetchBenchAICommentary() {
  const box  = document.getElementById('bench-ai-commentary');
  const body = document.getElementById('bench-ai-commentary-body');
  if (!box || !body) return;
  box.style.display = 'block';

  const myH      = benchmarkData.hotels.find(h => h.id === benchState.myHotelId);
  const compNames = [...benchState.compSet].map(id => benchmarkData.hotels.find(h => h.id === id)?.name).filter(Boolean).join(', ');
  const my   = aggDaily(getMyDaily());
  const comp = aggDaily(getCompDaily());

  const prompt = `Brief strategic commentary on ${myH?.name} vs comp set (${compNames || 'none'}) — Marrakech Luxury, last ${benchState.dateRange} days.
MY: Occ ${(my.occupancy*100).toFixed(1)}% | ADR MAD ${Math.round(my.adr).toLocaleString('en')} | RevPAR MAD ${Math.round(my.revpar).toLocaleString('en')}
COMP AVG: Occ ${(comp.occupancy*100).toFixed(1)}% | ADR MAD ${Math.round(comp.adr).toLocaleString('en')} | RevPAR MAD ${Math.round(comp.revpar).toLocaleString('en')}
2-3 sentences of strategic commentary. Cite specific numbers. Be direct.`;

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: [{ role: 'user', content: prompt }] }),
    });
    const data = await res.json();
    if (data.response) {
      body.className = 'bench-ai-content';
      body.innerHTML = mdRender(data.response);
    } else {
      box.style.display = 'none';
    }
  } catch {
    box.style.display = 'none';
  }
}

function renderBenchAIInsights() {
  renderBenchInsightCards();
  fetchBenchAICommentary();
}

// Date range pill events
document.getElementById('bench-date-bar').addEventListener('click', e => {
  const btn = e.target.closest('.bench-date-pill');
  if (!btn) return;
  document.querySelectorAll('.bench-date-pill').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  const v = btn.dataset.brange;
  benchState.dateRange = isNaN(Number(v)) ? v : Number(v);
  // Sync export period dropdown to match active date pill
  const periodEl = document.getElementById('bench-export-period');
  if (periodEl) periodEl.value = v;
  renderBenchAll();
});

// AI refresh button
document.getElementById('bench-ai-refresh').addEventListener('click', renderBenchAIInsights);

// ─── Global Search ────────────────────────────────────────────────

const searchIndex = { hotels: [], brands: [], cities: [], pipeline: [], news: [] };
let _srchDebounce = null;
let _srchActiveIdx = -1;

function buildSearchIndex() {
  if (hotels && hotels.length) {
    searchIndex.hotels = hotels.map(h => ({
      id: h.id,
      name: h.name || '',
      city: h.city || '',
      category: h.category || '',
      brand_group: h.brand_group || '',
      keys: h.keys || 0,
      searchText: `${h.name || ''} ${h.city || ''} ${h.brand_group || ''} ${h.owner || ''}`.toLowerCase(),
    }));

    const cityMap = {};
    hotels.forEach(h => { if (h.city) cityMap[h.city] = (cityMap[h.city] || 0) + 1; });
    searchIndex.cities = Object.entries(cityMap)
      .map(([city, count]) => ({ city, count, searchText: city.toLowerCase() }))
      .sort((a, b) => b.count - a.count);

    const brandMap = {};
    hotels.forEach(h => { if (h.brand_group) brandMap[h.brand_group] = (brandMap[h.brand_group] || 0) + 1; });
    searchIndex.brands = Object.entries(brandMap)
      .map(([brand, count]) => ({ brand, count, searchText: brand.toLowerCase() }))
      .sort((a, b) => b.count - a.count);
  }

  if (pipelineData) {
    searchIndex.pipeline = pipelineData.map(p => ({
      id: p.id,
      name: p.name || '',
      city: p.city || '',
      brand: p.brand || '',
      expected_opening: p.expected_opening || '',
      status: p.status || '',
      searchText: `${p.name || ''} ${p.city || ''} ${p.brand || ''}`.toLowerCase(),
    }));
  }

  if (newsData) {
    const articles = newsData.all || [];
    searchIndex.news = articles.map(a => ({
      id: a.id,
      title: a.title || '',
      category: a.category || '',
      date: a.date || '',
      searchText: `${a.title || ''} ${a.excerpt || ''}`.toLowerCase(),
    }));
  }
}

function _srchRun(query) {
  const q = query.toLowerCase().trim();
  if (q.length < 2) return null;
  return {
    hotels:   searchIndex.hotels.filter(h => h.searchText.includes(q)).slice(0, 4),
    brands:   searchIndex.brands.filter(b => b.searchText.includes(q)).slice(0, 3),
    cities:   searchIndex.cities.filter(c => c.searchText.includes(q)).slice(0, 3),
    pipeline: searchIndex.pipeline.filter(p => p.searchText.includes(q)).slice(0, 3),
    news:     searchIndex.news.filter(a => a.searchText.includes(q)).slice(0, 2),
  };
}

function _srchGetRecents() {
  try { return JSON.parse(localStorage.getItem('kodo_search_recents') || '[]'); } catch { return []; }
}
function _srchSaveRecent(q) {
  if (!q || q.length < 2) return;
  let r = _srchGetRecents().filter(x => x !== q);
  r.unshift(q);
  try { localStorage.setItem('kodo_search_recents', JSON.stringify(r.slice(0, 5))); } catch {}
}
function _srchRemoveRecent(q) {
  try { localStorage.setItem('kodo_search_recents', JSON.stringify(_srchGetRecents().filter(x => x !== q))); } catch {}
}
function _srchClearRecents() {
  try { localStorage.removeItem('kodo_search_recents'); } catch {}
}

function openSearch() {
  const overlay = document.getElementById('search-overlay');
  if (!overlay) return;
  overlay.classList.add('open');
  document.body.style.overflow = 'hidden';
  const input = document.getElementById('search-input');
  if (input) { input.value = ''; input.focus(); }
  _srchActiveIdx = -1;
  _srchRender('');
}

function closeSearch() {
  const overlay = document.getElementById('search-overlay');
  if (!overlay) return;
  overlay.classList.remove('open');
  document.body.style.overflow = '';
  _srchActiveIdx = -1;
}

function _srchNavigate(dir) {
  const container = document.getElementById('search-results');
  if (!container) return;
  const items = container.querySelectorAll('.search-result-item');
  if (!items.length) return;
  items[_srchActiveIdx]?.classList.remove('srch-active');
  _srchActiveIdx = (_srchActiveIdx + dir + items.length) % items.length;
  items[_srchActiveIdx].classList.add('srch-active');
  items[_srchActiveIdx].scrollIntoView({ block: 'nearest' });
}

function _srchSelectActive() {
  const active = document.querySelector('#search-results .srch-active');
  if (active) active.click();
}

function _srchNavigateToScreen(screen) {
  const link = document.querySelector(`.nav-link[data-screen="${screen}"]`);
  if (link) link.click();
}

function _srchRender(query) {
  const container = document.getElementById('search-results');
  const clearBtn  = document.getElementById('search-clear-btn');
  if (!container) return;
  _srchActiveIdx = -1;
  clearBtn?.classList.toggle('visible', query.length > 0);

  if (!query) {
    const recents = _srchGetRecents();
    if (!recents.length) {
      container.innerHTML = '<div class="search-empty">Type to search hotels, brands, cities, and more</div>';
      return;
    }
    const header = document.createElement('div');
    header.className = 'search-recents-header';
    header.innerHTML = '<span class="search-recents-label">Recent Searches</span>';
    const clearAll = document.createElement('button');
    clearAll.className = 'search-clear-all';
    clearAll.textContent = 'Clear all';
    clearAll.addEventListener('click', () => { _srchClearRecents(); _srchRender(''); });
    header.appendChild(clearAll);
    container.innerHTML = '';
    container.appendChild(header);
    recents.forEach(r => {
      const item = document.createElement('div');
      item.className = 'search-recent-item';
      item.innerHTML = `
        <span class="search-recent-text">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="opacity:0.45;flex-shrink:0"><circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 15 15"/></svg>
          ${fmt.esc(r)}
        </span>
        <button class="search-recent-remove" aria-label="Remove">&times;</button>`;
      item.querySelector('.search-recent-remove').addEventListener('click', e => {
        e.stopPropagation();
        _srchRemoveRecent(r);
        _srchRender('');
      });
      item.addEventListener('click', () => {
        const inp = document.getElementById('search-input');
        if (inp) inp.value = r;
        _srchRender(r);
      });
      container.appendChild(item);
    });
    return;
  }

  if (query.length < 2) {
    container.innerHTML = '<div class="search-empty">Type at least 2 characters to search</div>';
    return;
  }

  const results = _srchRun(query);
  const groups = [];

  if (results.hotels.length) groups.push({
    label: 'Hotels',
    items: results.hotels.map(h => ({
      name: h.name,
      meta: [h.city, h.category, h.keys ? h.keys.toLocaleString() + ' keys' : ''].filter(Boolean).join(' · '),
      action() { closeSearch(); _srchSaveRecent(query); showHotelDetail(h.id); },
    })),
  });

  if (results.brands.length) groups.push({
    label: 'Brands',
    items: results.brands.map(b => ({
      name: b.brand,
      meta: `${b.count} ${b.count === 1 ? 'hotel' : 'hotels'}`,
      action() { closeSearch(); _srchSaveRecent(query); showBrandDetail(b.brand, 'dashboard'); },
    })),
  });

  if (results.cities.length) groups.push({
    label: 'Cities',
    items: results.cities.map(c => ({
      name: c.city,
      meta: `${c.count} ${c.count === 1 ? 'hotel' : 'hotels'}`,
      action() {
        closeSearch(); _srchSaveRecent(query);
        _srchNavigateToScreen('dashboard');
        const sidebarItem = document.querySelector(`#city-filter .sidebar-item[data-city="${c.city}"]`);
        if (sidebarItem) sidebarItem.click();
      },
    })),
  });

  if (results.pipeline.length) groups.push({
    label: 'Pipeline',
    items: results.pipeline.map(p => ({
      name: p.name,
      meta: [p.city, p.expected_opening, p.status].filter(Boolean).join(' · '),
      action() { closeSearch(); _srchSaveRecent(query); _srchNavigateToScreen('pipeline'); },
    })),
  });

  if (results.news.length) groups.push({
    label: 'News',
    items: results.news.map(a => ({
      name: a.title,
      meta: [a.category, a.date].filter(Boolean).join(' · '),
      action() {
        closeSearch(); _srchSaveRecent(query);
        _srchNavigateToScreen('news');
        setTimeout(() => showArticleDetail(a.id), 350);
      },
    })),
  });

  if (!groups.length) {
    container.innerHTML = `<div class="search-empty">No results for &ldquo;${fmt.esc(query)}&rdquo;</div>`;
    return;
  }

  container.innerHTML = '';
  groups.forEach((g, gi) => {
    const groupEl = document.createElement('div');
    groupEl.className = 'search-group';
    const labelEl = document.createElement('div');
    labelEl.className = 'search-group-label';
    labelEl.textContent = g.label;
    groupEl.appendChild(labelEl);
    g.items.forEach(item => {
      const el = document.createElement('div');
      el.className = 'search-result-item';
      el.innerHTML = `<div class="search-result-name">${fmt.esc(item.name)}</div><div class="search-result-meta">${fmt.esc(item.meta)}</div>`;
      el.addEventListener('click', item.action);
      groupEl.appendChild(el);
    });
    container.appendChild(groupEl);
  });
}

// Search event wiring
(function initSearchEvents() {
  const input   = document.getElementById('search-input');
  const clearBtn = document.getElementById('search-clear-btn');
  const overlay = document.getElementById('search-overlay');

  input?.addEventListener('input', () => {
    clearTimeout(_srchDebounce);
    _srchDebounce = setTimeout(() => _srchRender(input.value.trim()), 150);
  });

  clearBtn?.addEventListener('click', () => {
    if (input) { input.value = ''; input.focus(); }
    _srchRender('');
  });

  overlay?.addEventListener('click', e => {
    if (e.target === overlay) closeSearch();
  });

  document.getElementById('search-nav-btn')?.addEventListener('click', openSearch);

  document.addEventListener('keydown', e => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      const ov = document.getElementById('search-overlay');
      if (ov?.classList.contains('open')) closeSearch(); else openSearch();
      return;
    }
    const ov = document.getElementById('search-overlay');
    if (!ov?.classList.contains('open')) return;
    if (e.key === 'Escape')    { closeSearch(); }
    else if (e.key === 'ArrowDown') { e.preventDefault(); _srchNavigate(1); }
    else if (e.key === 'ArrowUp')   { e.preventDefault(); _srchNavigate(-1); }
    else if (e.key === 'Enter')     { e.preventDefault(); _srchSelectActive(); }
  });
})();

// ─── Boot ─────────────────────────────────────────────────────────

async function boot() {
  [apiData, hotels] = await Promise.all([
    fetch('/api/data').then(r => r.json()),
    fetch('/api/hotels').then(r => r.json()),
  ]);
  buildCityFilter();
  buildCityPills();
  buildSegPills();
  buildMobileCityPills();
  render();
  buildSearchIndex();
}

// Fetch current user info and populate tier badge
fetch('/api/me').then(r => r.ok ? r.json() : null).then(me => {
  if (!me) return;
  const badge = document.getElementById('tier-badge');
  if (!badge) return;
  const label = { observer: 'Observer', benchmarker: 'Benchmarker', advisory: 'Advisory' }[me.tier] || me.tier;
  badge.textContent = label;
  badge.className = `tier-badge tier-badge--${me.tier}`;
  badge.style.display = '';
  window._kodoUser = me;
  // Hide export buttons and dropdowns for Observer tier
  if (me.tier === 'observer') {
    document.querySelectorAll(
      '.export-btn, #bench-export-period, #tourism-export-year'
    ).forEach(el => { el.style.display = 'none'; });
  }
});

// ── Reports ──────────────────────────────────────────────────────────────────
let reportsInited = false;

async function initReports() {
  if (reportsInited) return;
  const grid = document.getElementById('reports-grid');
  if (!grid) return;

  const tier = (window._kodoUser && window._kodoUser.tier) || '';
  const canGenerate = tier === 'benchmarker' || tier === 'advisory';

  try {
    const res = await fetch('/api/reports/available');
    if (!res.ok) return;
    const data = await res.json();

    grid.innerHTML = '';
    const allCities = data.cities || [];

    allCities.forEach(cityMeta => {
      const card = document.createElement('div');
      card.style.cssText = 'background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:20px 22px;transition:border-color 0.15s;';

      const periodsHTML = (data.periods || []).map((p, i) =>
        `<button class="report-period-pill ${i===0?'active':''}" data-period="${p}"
          style="padding:4px 10px;border-radius:3px;border:1px solid var(--border);font-size:0.6875rem;cursor:pointer;
          background:${i===0?'var(--accent)':'var(--surface)'};color:${i===0?'#0A0A0A':'var(--muted)'};
          font-family:'Plus Jakarta Sans',sans-serif;transition:all 0.12s;">${p}</button>`
      ).join('');

      const lockIcon = canGenerate ? '' : '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:5px;vertical-align:middle"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>';

      card.innerHTML = `
        <div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:600;color:var(--text);margin-bottom:3px;">${cityMeta.city}</div>
        <div style="font-size:0.75rem;color:var(--muted);margin-bottom:12px;">Morocco Hotel Market</div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px;" class="report-period-pills">${periodsHTML}</div>
        <div style="display:flex;gap:6px;margin-bottom:12px;" class="report-theme-pills">
          <button class="report-theme-pill active" data-theme="dark"
            style="padding:4px 10px;border-radius:3px;border:1px solid var(--accent);font-size:0.6875rem;cursor:pointer;
            background:var(--accent);color:#0A0A0A;font-family:'Plus Jakarta Sans',sans-serif;transition:all 0.12s;">◐ Dark</button>
          <button class="report-theme-pill" data-theme="light"
            style="padding:4px 10px;border-radius:3px;border:1px solid var(--border);font-size:0.6875rem;cursor:pointer;
            background:var(--surface);color:var(--muted);font-family:'Plus Jakarta Sans',sans-serif;transition:all 0.12s;">○ Light</button>
        </div>
        <div style="font-size:0.6875rem;color:var(--text-faint,#888);margin-bottom:12px;">${cityMeta.hotels} hotels tracked · ${cityMeta.keys?.toLocaleString() || '—'} keys</div>
        <button class="report-generate-btn" data-city="${cityMeta.city}"
          style="width:100%;padding:9px;background:${canGenerate?'var(--accent)':'var(--border)'};
          color:${canGenerate?'#0A0A0A':'var(--muted)'};border:none;cursor:pointer;
          font-family:'Syne',sans-serif;font-size:0.75rem;font-weight:600;letter-spacing:0.05em;text-transform:uppercase;
          display:flex;align-items:center;justify-content:center;">
          ${lockIcon}Generate Dark Report
        </button>
        <div class="report-status" style="font-size:0.75rem;color:var(--muted);margin-top:8px;min-height:18px;text-align:center;"></div>
      `;

      // Period pill switching
      card.querySelectorAll('.report-period-pill').forEach(pill => {
        pill.addEventListener('click', () => {
          card.querySelectorAll('.report-period-pill').forEach(p => {
            p.style.background = 'var(--surface)';
            p.style.color = 'var(--muted)';
            p.style.borderColor = 'var(--border)';
            p.classList.remove('active');
          });
          pill.style.background = 'var(--accent)';
          pill.style.color = '#0A0A0A';
          pill.classList.add('active');
        });
      });

      // Theme pill switching
      const updateGenBtn = () => {
        const activeTheme = card.querySelector('.report-theme-pill.active')?.dataset.theme || 'dark';
        const btn = card.querySelector('.report-generate-btn');
        if (btn && !btn.disabled) {
          const label = activeTheme === 'dark' ? 'Generate Dark Report' : 'Generate Light Report';
          btn.innerHTML = `${lockIcon}${label}`;
        }
      };
      card.querySelectorAll('.report-theme-pill').forEach(pill => {
        pill.addEventListener('click', () => {
          card.querySelectorAll('.report-theme-pill').forEach(p => {
            p.style.background = 'var(--surface)';
            p.style.color = 'var(--muted)';
            p.style.borderColor = 'var(--border)';
            p.classList.remove('active');
          });
          pill.style.background = 'var(--accent)';
          pill.style.color = '#0A0A0A';
          pill.style.borderColor = 'var(--accent)';
          pill.classList.add('active');
          updateGenBtn();
        });
      });

      // Hover border
      card.addEventListener('mouseenter', () => { card.style.borderColor = 'var(--accent)'; });
      card.addEventListener('mouseleave', () => { card.style.borderColor = 'var(--border)'; });

      // Generate button
      card.querySelector('.report-generate-btn').addEventListener('click', async () => {
        if (!canGenerate) {
          showUpgradeModal('Benchmarker & Advisory Only', 'Reports are available on Benchmarker and Advisory plans. Upgrade to download institutional-grade PDF market reports.');
          return;
        }
        const city   = cityMeta.city;
        const period = card.querySelector('.report-period-pill.active')?.dataset.period || data.periods[0];
        const theme  = card.querySelector('.report-theme-pill.active')?.dataset.theme || 'dark';
        const btn    = card.querySelector('.report-generate-btn');
        const status = card.querySelector('.report-status');

        btn.disabled = true;
        btn.textContent = 'Generating…';
        btn.style.opacity = '0.6';
        status.textContent = 'Generating your report… this may take 30–60 seconds';

        try {
          const r = await fetch('/api/reports/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({city, period, theme}),
          });

          if (!r.ok) {
            const err = await r.json().catch(() => ({error: 'Unknown error'}));
            throw new Error(err.error || 'Generation failed');
          }

          const blob  = await r.blob();
          const url   = URL.createObjectURL(blob);
          const a     = document.createElement('a');
          const safe  = city.replace(/ \/ /g, '-').replace(/ /g, '-');
          const safep = period.replace(/ /g, '-');
          a.href      = url;
          a.download  = `Kodo_${safe}_${safep}_${theme}.pdf`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          URL.revokeObjectURL(url);

          status.textContent = '✓ Report ready — downloading now';
          status.style.color = 'var(--positive, #2D6B3A)';
        } catch (err) {
          status.textContent = `Error: ${err.message}`;
          status.style.color = 'var(--negative, #8B3A3A)';
        } finally {
          btn.disabled = false;
          btn.style.opacity = '1';
          updateGenBtn();
        }
      });

      grid.appendChild(card);
    });

    reportsInited = true;
  } catch (e) {
    console.error('initReports error:', e);
  }
}

// ─── Excel Export ─────────────────────────────────────────────────────────────

function canExport() {
  const tier = (window._kodoUser && window._kodoUser.tier) || '';
  return tier === 'benchmarker' || tier === 'advisory';
}

function exportToExcel(sheets, filename) {
  const wb = XLSX.utils.book_new();
  const autoW = data => Object.keys(data[0] || {}).map(k => ({
    wch: Math.max(k.length, ...data.map(r => String(r[k] ?? '').length))
  }));
  sheets.forEach(({ data, name }) => {
    if (!data || !data.length) return;
    const ws = XLSX.utils.json_to_sheet(data);
    ws['!cols'] = autoW(data);
    XLSX.utils.book_append_sheet(wb, ws, name);
  });
  const about = [{
    'Source':    'Kōdō Hospitality — Morocco Hotel Market Intelligence',
    'Website':   'kodohospitality.com',
    'Generated': new Date().toLocaleDateString('en-GB'),
    'Note':      'Kōdō proprietary estimates unless marked Verified',
    'Contact':   'advisory@kodohospitality.com',
  }];
  const wsAbout = XLSX.utils.json_to_sheet(about);
  wsAbout['!cols'] = Object.keys(about[0]).map(k => ({
    wch: Math.max(k.length, ...about.map(r => String(r[k] ?? '').length))
  }));
  XLSX.utils.book_append_sheet(wb, wsAbout, 'About');
  XLSX.writeFile(wb, filename + '.xlsx');
}

function exportHotels() {
  if (!canExport()) {
    showUpgradeModal('Benchmarker & Advisory Only', 'Excel export is available on Benchmarker and Advisory plans. Upgrade to download hotel directory data.');
    return;
  }
  const filtered = filterHotels();
  if (!filtered.length) return;
  const date = new Date().toISOString().split('T')[0];
  const cityLabel = hotelsState.city !== 'all' ? hotelsState.city.replace(/[^a-zA-Z0-9]/g, '_') : 'All';
  const data = filtered.map(h => ({
    'Hotel Name':       h.name,
    'City':             h.city,
    'Segment':          h.category,
    'Brand Group':      h.brand_group,
    'Keys':             h.keys,
    'Occupancy %':      h.occupancy ? (h.occupancy * 100).toFixed(1) + '%' : 'N/A',
    'ADR (MAD)':        h.adr_mad || 'N/A',
    'RevPAR (MAD)':     h.revpar_mad || 'N/A',
    'Year Established': h.year_opened_verified === 'verified' ? h.year_opened : 'N/A',
    'Owner':            h.owner || 'Undisclosed',
    'Data Quality':     h.data_quality || 'Kōdō Estimate',
  }));
  exportToExcel([{ data, name: 'Hotels' }], `Kodo_Hotels_${cityLabel}_${date}`);
}

function exportPipeline() {
  if (!canExport()) {
    showUpgradeModal('Benchmarker & Advisory Only', 'Excel export is available on Benchmarker and Advisory plans. Upgrade to download pipeline data.');
    return;
  }
  if (!pipelineData) return;
  const date = new Date().toISOString().split('T')[0];
  const data = filteredPipeline().map(p => ({
    'Project Name':       p.name,
    'City':               p.city,
    'Category':           p.category,
    'Brand':              p.brand,
    'Brand Group':        p.brand_group,
    'Keys':               p.keys || 'TBC',
    'Expected Opening':   p.expected_opening,
    'Status':             p.status,
    'Investment (MAD M)': p.investment_mad ? Math.round(p.investment_mad / 1e6) : 'N/A',
  }));
  exportToExcel([{ data, name: 'Pipeline' }], `Kodo_Pipeline_${date}`);
}

function exportBrands() {
  if (!canExport()) {
    showUpgradeModal('Benchmarker & Advisory Only', 'Excel export is available on Benchmarker and Advisory plans. Upgrade to download brand performance data.');
    return;
  }
  if (!brandsData) return;
  const date = new Date().toISOString().split('T')[0];
  const data = filteredBrands().map((b, i) => ({
    'Rank':              i + 1,
    'Brand Group':       b.brand_group,
    'Hotels':            b.hotels,
    'Total Keys':        b.total_keys,
    'Market Share %':    b.market_share_keys_pct != null ? b.market_share_keys_pct.toFixed(1) + '%' : 'N/A',
    'Avg Occupancy %':   b.avg_occupancy ? (b.avg_occupancy * 100).toFixed(1) + '%' : 'N/A',
    'Avg ADR (MAD)':     b.avg_adr ? Math.round(b.avg_adr) : 'N/A',
    'Avg RevPAR (MAD)':  b.weighted_revpar ? Math.round(b.weighted_revpar) : 'N/A',
    'Cities Present':    Array.isArray(b.cities) ? b.cities.join(', ') : 'N/A',
    'Pipeline Projects': b.pipeline_projects || 0,
    'Pipeline Keys':     b.pipeline_keys || 0,
  }));
  exportToExcel([{ data, name: 'Brand Performance' }], `Kodo_Brands_${date}`);
}

function exportBenchmarking() {
  if (!canExport()) {
    showUpgradeModal('Benchmarker & Advisory Only', 'Excel export is available on Benchmarker and Advisory plans. Upgrade to download benchmarking data.');
    return;
  }
  if (!benchmarkData) return;
  const date     = new Date().toISOString().split('T')[0];
  const myH      = benchmarkData.hotels.find(h => h.id === benchState.myHotelId);
  const propName = myH ? myH.name.replace(/[^a-zA-Z0-9]/g, '_') : 'Property';
  const valid    = isCompSetValid();

  // Read selected export period from dropdown (default to active date pill)
  const periodEl  = document.getElementById('bench-export-period');
  const periodVal = periodEl ? periodEl.value : String(benchState.dateRange);
  const periodMap = { '7': 'Last_7_Days', '30': 'Last_30_Days', '90': 'Last_90_Days', 'ytd': 'YTD' };
  const periodLabel = periodMap[periodVal] || 'Period';
  const periodDisp  = periodEl ? periodEl.options[periodEl.selectedIndex]?.text : String(benchState.dateRange);

  // Sheet 1 — KPI Summary
  const my   = aggDaily(getMyDaily());
  const comp = aggDaily(getCompDaily());
  const mkIdx = (myV, compV) => (valid && compV > 0) ? Math.round(myV / compV * 100) : 'N/A';
  const kpiData = [
    { 'Metric': 'Occupancy %',  'My Property': (my.occupancy * 100).toFixed(1) + '%',
      'Comp Set Average': valid ? (comp.occupancy * 100).toFixed(1) + '%' : 'N/A',
      'Index': mkIdx(my.occupancy, comp.occupancy), 'Period': periodDisp },
    { 'Metric': 'ADR (MAD)',    'My Property': Math.round(my.adr),
      'Comp Set Average': valid ? Math.round(comp.adr) : 'N/A',
      'Index': mkIdx(my.adr, comp.adr), 'Period': periodDisp },
    { 'Metric': 'RevPAR (MAD)', 'My Property': Math.round(my.revpar),
      'Comp Set Average': valid ? Math.round(comp.revpar) : 'N/A',
      'Index': mkIdx(my.revpar, comp.revpar), 'Period': periodDisp },
  ];

  // Sheet 2 — Monthly Detail (mirrors renderBenchMonthlyTable)
  const months = {};
  benchmarkData.daily.forEach(d => {
    const mk = d.date.substring(0, 7);
    if (!months[mk]) months[mk] = { my: [], compByDate: {} };
    if (d.hotel_id === benchState.myHotelId) {
      months[mk].my.push(d);
    } else if (benchState.compSet.has(d.hotel_id)) {
      if (!months[mk].compByDate[d.date]) months[mk].compByDate[d.date] = [];
      months[mk].compByDate[d.date].push(d);
    }
  });
  const MON = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const monthlyData = Object.keys(months).sort().map(mk => {
    const { my: myRecs, compByDate } = months[mk];
    const myAgg    = aggDaily(myRecs);
    const compAvgs = Object.values(compByDate).map(recs => aggDaily(recs));
    const compAgg  = aggDaily(compAvgs);
    const noComp   = !valid || !compAvgs.length;
    const revIdx   = (!noComp && compAgg.revpar > 0) ? Math.round(myAgg.revpar / compAgg.revpar * 100) : 'N/A';
    const [yr, mo] = mk.split('-');
    return {
      'Month':                `${MON[Number(mo) - 1]} ${yr}`,
      'My Occupancy %':       (myAgg.occupancy * 100).toFixed(1) + '%',
      'Comp Set Occupancy %': noComp ? 'N/A' : (compAgg.occupancy * 100).toFixed(1) + '%',
      'My ADR (MAD)':         Math.round(myAgg.adr),
      'Comp Set ADR (MAD)':   noComp ? 'N/A' : Math.round(compAgg.adr),
      'My RevPAR (MAD)':      Math.round(myAgg.revpar),
      'Comp Set RevPAR (MAD)':noComp ? 'N/A' : Math.round(compAgg.revpar),
      'RevPAR Index':         revIdx,
    };
  });

  exportToExcel(
    [
      { data: kpiData, name: 'KPI Summary' },
      { data: monthlyData.length ? monthlyData : [{ 'Note': 'No monthly data available' }], name: 'Monthly Detail' },
    ],
    `Kodo_Benchmarking_${propName}_${periodLabel}_${date}`
  );
}

function exportTourism() {
  if (!canExport()) {
    showUpgradeModal('Benchmarker & Advisory Only', 'Excel export is available on Benchmarker and Advisory plans. Upgrade to download tourism intelligence data.');
    return;
  }
  const yearEl = document.getElementById('tourism-export-year');
  const year   = yearEl ? yearEl.value : '2025';
  const yearNum = parseInt(year, 10);

  // Sheet 1 — International Arrivals (all years with YoY growth, filtered to selected year)
  const ARR_YEARS = ['2020','2021','2022','2023','2024','2025','2026E'];
  const ARR_VALS  = [2.3, 5.2, 11.0, 14.5, 17.4, 20.1, 22.5];
  const arrivalsData = ARR_YEARS
    .filter(yr => yr === year)
    .map(yr => {
      const idx  = ARR_YEARS.indexOf(yr);
      const prev = idx > 0 ? ARR_VALS[idx - 1] : null;
      const growth = prev ? ((ARR_VALS[idx] - prev) / prev * 100).toFixed(1) + '%' : 'N/A';
      return { 'Year': yr, 'Total Arrivals (M)': ARR_VALS[idx], 'YoY Growth %': growth };
    });

  // Sheet 2 — Airport Traffic for selected year
  const airYearVals = TOUR_AIRPORT_DATA.years[yearNum];
  const airportData = airYearVals
    ? TOUR_AIRPORT_DATA.labels.map((airport, i) => ({
        'Airport': airport,
        'Passengers (M)': airYearVals[i],
        'Year': year,
      }))
    : TOUR_AIRPORT_DATA.labels.map((airport, i) => {
        const row = { 'Airport': airport };
        Object.entries(TOUR_AIRPORT_DATA.years).forEach(([yr, vals]) => { row[`${yr} (M pax)`] = vals[i]; });
        return row;
      });

  // Sheet 3 — Origin Markets for selected year
  const origYearVals = TOUR_ORIGINS_DATA.years[yearNum];
  const originsData = origYearVals
    ? TOUR_ORIGINS_DATA.labels.map((origin, i) => ({
        'Country': origin,
        'Arrivals Share %': origYearVals[i] + '%',
        'Year': year,
      }))
    : TOUR_ORIGINS_DATA.labels.map((origin, i) => {
        const row = { 'Origin Market': origin };
        Object.entries(TOUR_ORIGINS_DATA.years).forEach(([yr, vals]) => { row[`${yr} (%)`] = vals[i]; });
        return row;
      });

  exportToExcel(
    [
      { data: arrivalsData.length ? arrivalsData : [{ 'Note': 'No data for selected year' }], name: 'International Arrivals' },
      { data: airportData, name: 'Airport Traffic' },
      { data: originsData, name: 'Origin Markets' },
    ],
    `Kodo_Tourism_Morocco_${year}`
  );
}

// Wire up export button clicks
document.getElementById('btn-export-hotels')  ?.addEventListener('click', exportHotels);
document.getElementById('btn-export-pipeline') ?.addEventListener('click', exportPipeline);
document.getElementById('btn-export-brands')   ?.addEventListener('click', exportBrands);
document.getElementById('btn-export-bench')    ?.addEventListener('click', exportBenchmarking);
document.getElementById('btn-export-tourism')  ?.addEventListener('click', exportTourism);

boot();
