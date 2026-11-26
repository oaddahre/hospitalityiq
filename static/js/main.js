// ─── Constants ────────────────────────────────────────────────────

const BRAND_DOMAINS = {
  'Accor': 'accor.com',
  'Hilton Hotels & Resorts': 'hilton.com',
  'Hyatt Hotels Corporation': 'hyatt.com',
  'RIU Hotels & Resorts': 'riu.com',
  'Barceló Hotel Group': 'barcelo.com',
  'Kenzi Hotels Group': 'kenzi-hotels.com',
  'Atlas Hotels Group': 'almada.ma',
  'View Hotels': 'almada.ma',
  'The View': 'almada.ma',
  'Terminus Hotels': 'almada.ma',
  'Mogador Hotels Group': 'mogadorhotels.com',
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
  'Lancaster Hotels': 'lancaster-hotel.com',
};

const LOCAL_BRAND_LOGOS = {
  'Mia Hotels': '/static/images/brands/mia_logo.png?v=2',
  'Zephyr': '/static/images/brands/zephyr_logo.png?v=2',
  'Story Hospitality': '/static/images/brands/story_logo.png?v=2',
  'Globalia Hotels': '/static/images/brands/globalia_logo.png?v=2',
  'Lancaster Hotels': '/static/images/brands/lancaster_logo.png?v=2',
  'Banyan Tree': '/static/images/brands/banyantree_logo.png?v=2',
  'Vichy Thermalia': '/static/images/brands/vichy_logo.png?v=2',
  'Valeria Hotels': '/static/images/brands/valeria_logo.png?v=2',
  'Pickalbatros': '/static/images/brands/pickalbatros_logo.png?v=2',
  // Official logos from each company's own website (Nov 2026; sources in
  // _handoff/logos/sources.json): trimmed, 200 px high, transparent
  "Accor": '/static/images/brands/accor_logo.png?v=2',
  "Aman Resorts": '/static/images/brands/aman_logo.png?v=2',
  "Barceló Hotel Group": '/static/images/brands/barcelo_logo.png?v=2',
  "Decameron Hotels & Resorts": '/static/images/brands/decameron_logo.png?v=2',
  "Hilton Hotels & Resorts": '/static/images/brands/hilton_logo.png?v=2',
  "Hotusa (Eurostars Hotel Company)": '/static/images/brands/eurostars_logo.png?v=2',
  "Hyatt Hotels Corporation": '/static/images/brands/hyatt_logo.png?v=2',
  "IHG Hotels & Resorts": '/static/images/brands/ihg_logo.png?v=3',
  "Kenzi Hotels Group": '/static/images/brands/kenzi_logo.png?v=2',
  "Mandarin Oriental Hotel Group": '/static/images/brands/mandarin_logo.png?v=2',
  "Mogador Hotels Group": '/static/images/brands/mogador_logo.png?v=2',
  "Nobu Hospitality": '/static/images/brands/nobu_logo.png?v=2',
  "Oberoi Hotels & Resorts": '/static/images/brands/oberoi_logo.png?v=2',
  "Pestana Hotel Group": '/static/images/brands/pestana_logo.png?v=2',
  "Relais & Châteaux": '/static/images/brands/relais_logo.png?v=2',
  "Royal Mansour Collection": '/static/images/brands/royalmansour_logo.png?v=2',
  "Soho Boutique Hotels": '/static/images/brands/soho_logo.png?v=2',
  "TUI Hotels & Resorts": '/static/images/brands/tui_logo.png?v=2',
  "Virgin Limited Edition": '/static/images/brands/virgin_logo.png?v=2',
  "Wyndham Hotels & Resorts": '/static/images/brands/wyndham_logo.png?v=2',
  "Xaluca Hotels": '/static/images/brands/xaluca_logo.png?v=2',
  // Official logos supplied in _handoff/logos/originals (25 Nov 2026; IHG
  // replaced the same day): trimmed, 200 px square on white
  "Marriott International": '/static/images/brands/marriott_logo.png?v=1',
  "Radisson Hotel Group": '/static/images/brands/radisson_logo.png?v=1',
  "The Ascott Limited": '/static/images/brands/ascott_logo.png?v=1',
  "Four Seasons Hotels & Resorts": '/static/images/brands/fourseasons_logo.png?v=1',   // tree symbol: the wordmark is unreadable at 40 px
  "Atlas Hospitality Group": '/static/images/brands/atlas_logo.png?v=1',               // "AHG" monogram, same reason
};

const BRAND_CUSTOM_LOGOS = {
  'Zalagh Hotels Group':         { letter: 'Z',  bg: 'var(--bg)', color: 'var(--cat-1-text)' },
  'Farah Hotels':                { letter: 'F',  bg: 'var(--bg)', color: 'var(--cat-1-text)' },
  'Independent Ultra Luxury':    { letter: 'UL', bg: 'var(--bg)', color: 'var(--cat-1-text)' },
  'Independent Luxury':          { letter: 'IL', bg: 'var(--bg)', color: 'var(--cat-1-text)' },
  'Independent Upper Upscale':   { letter: 'UU', bg: 'var(--bg)', color: 'var(--text-2)' },
  'Independent Upscale':         { letter: 'IU', bg: 'var(--bg)', color: 'var(--text-2)' },
  'Independent Midscale':        { letter: 'IM', bg: 'var(--bg)', color: 'var(--text-2)' },
  'Independent Economy':         { letter: 'IE', bg: 'var(--bg)', color: 'var(--text-2)' },

  'Zephyr':                      { letter: 'Z',  bg: 'var(--bg)', color: 'var(--cat-1-text)' },
};

const OWNER_LOGOS = {
  'Madaëf': '/static/images/brands/madaef_logo.png?v=2',
  'Risma': '/static/images/brands/risma_logo.png?v=2',
  'Valeria Hotels': '/static/images/brands/valeria_logo.png?v=2',
  'Tikida Group': '/static/images/brands/tikida_logo.png?v=2',
  'Pickalbatros': '/static/images/brands/pickalbatros_logo.png?v=2',
  'OCP Group': '/static/images/brands/ocp_logo.png?v=2',
  "Barceló Hotel Group": '/static/images/brands/barcelo_logo.png?v=2',
  "Kenzi Hotels Group": '/static/images/brands/kenzi_logo.png?v=2',
  "Al Mada": '/static/images/brands/almada_logo.png?v=2',
  "Babylon Invest": '/static/images/brands/babylon_logo.png?v=2',
  "Inveravante": '/static/images/brands/inveravante_logo.png?v=2',
  "Ynna Holding": '/static/images/brands/ynna_logo.png?v=2',
  "Beachcomber": '/static/images/brands/beachcomber_logo.png?v=2',
};

const OWNER_LOGO_DOMAINS = {
  'Risma': 'risma.ma',
  'Al Mada': 'almada.ma',
  'Kenzi Hotels Group': 'kenzi-hotels.com',
};

// Every logo sits in the same square tile, in every list, card, page and
// search result: `size` square, white in both themes (readable on the pure
// black dark-mode page too), corner radius from the size. The logo files
// are square already (512 px, the mark centred with 12% padding), so wide
// wordmarks and square marks line up. A brand or owner without a logo, or
// one whose image fails to load, shows its initials in the same tile.
const tileRadius = size => Math.max(3, Math.round(size * 0.2));
function logoChipImg(src, alt, size, gap, fallbackHtml) {
  const fb = fallbackHtml ? ` data-fallback="${encodeURIComponent(fallbackHtml)}"` : '';
  return `<img class="logo-tile" src="${src}" alt="${fmt.esc(alt)}"${fb} width="${size}" height="${size}" loading="lazy"`
    + ` style="width:${size}px;height:${size}px;padding:${Math.max(1, Math.round(size * 0.04))}px;border-radius:${tileRadius(size)}px;margin-right:${gap || 0}px" onerror="logoFallback(this)">`;
}
function logoFallback(img) {
  const fb = img.dataset.fallback;
  if (fb) img.outerHTML = decodeURIComponent(fb); else img.style.display = 'none';
}
// Initials in the logo tile: tinted, same size and radius as a logo
function initialsTile(text, size, gap, bg, color) {
  return `<span class="logo-tile logo-tile--initials brn-initials" style="width:${size}px;height:${size}px;border-radius:${tileRadius(size)}px;`
    + `background:${bg || 'var(--cat-1-tint)'};color:${color || 'var(--cat-1-text)'};font-size:${Math.max(7, Math.round(size * (text.length > 1 ? 0.36 : 0.5)))}px;margin-right:${gap || 0}px">${fmt.esc(text)}</span>`;
}
function ownerInitials(ownerName, size, gap = 10) {
  const initials = ownerName.split(/\s+/).filter(w => /[A-Za-zÀ-ÿ]/.test(w[0] || '')).map(w => w[0]).join('').substring(0, 2).toUpperCase();
  return initialsTile(initials, size, gap);
}

function getOwnerLogoImg(ownerName, size) {
  size = size || 40;
  var localLogo = OWNER_LOGOS[ownerName];
  var domainLogo = OWNER_LOGO_DOMAINS[ownerName];
  var src = localLogo || (domainLogo && 'https://cdn.brandfetch.io/domain/' + domainLogo + '?c=1idptYpdMe9b8BdTIPC');
  return src ? logoChipImg(src, ownerName, size, 10, ownerInitials(ownerName, size)) : ownerInitials(ownerName, size);
}

// Colour families from static/css/tokens.css — the single source of truth
// for every coloured label platform-wide. A label is a span with a
// .pill--<family> class (tint, text colour, dot); dots and chart marks read
// the family's bright dot colour through familyDot().
const FAMILY_INDEX = { blue: 1, green: 2, orange: 3, violet: 4, sky: 5, grey: 6, red: 7 };

function familyDot(family) {
  return getComputedStyle(document.documentElement)
    .getPropertyValue('--cat-' + (FAMILY_INDEX[family] || 6) + '-dot').trim();
}

// Heat cells: the family's dot colour mixed into the page colour at four
// strengths; the text stays --text, which is AA on every level in both modes.
const HEAT_LEVELS = [8, 20, 35, 55];
function heatCell(family, level, fw) {
  return {
    bg: `color-mix(in srgb, var(--cat-${FAMILY_INDEX[family] || 6}-dot) ${HEAT_LEVELS[level]}%, var(--bg))`,
    col: 'var(--text)', fw: fw || '', border: '',
  };
}
const HEAT_EMPTY = { bg: 'var(--bg)', col: 'var(--text-2)', fw: '', border: '1px dashed var(--border)' };

function pillHtml(family, text, cls) {
  return `<span class="${cls ? cls + ' ' : ''}pill--${family}">${fmt.esc(text)}</span>`;
}

// Owners: State = grey, Listed = blue, Private = green, Family = orange
const OWNER_TYPE_FAMILY = {
  'State-Owned':  'grey',
  'Listed':       'blue',
  'Private':      'green',
  'Family-Owned': 'orange',
};

function ownerTypeBadge(type) {
  if (type === 'Undisclosed') return '';          // type not known: no badge rather than a guess
  return pillHtml(OWNER_TYPE_FAMILY[type] || 'green', type, 'owner-type-badge');
}

// "OCP Group (via Maghreb Hospitality Company)": the owner and, when its
// profile says so, the company it holds the hotel through (owner_via)
function ownerText(h) {
  return h.owner_via ? `${h.owner} (via ${h.owner_via})` : (h.owner || '');
}

// Hotel segments
const SEGMENT_FAMILY = {
  'Ultra Luxury':  'violet',
  'Luxury':        'blue',
  'Upper Upscale': 'sky',
  'Upscale':       'green',
  'Midscale':      'orange',
  'Economy':       'grey',
};

const BRAND_DESCRIPTIONS = {
  'Marriott International': "Marriott International is the world's largest hotel company with over 30 brands and 9,000 properties across 140 countries. In Morocco, Marriott operates through flagship brands including Marriott Hotels, Sheraton, Courtyard, Four Points, and the ultra-luxury St. Regis and Ritz-Carlton. The group has been present in Morocco since 1989 and continues to expand with confirmed pipeline projects in Marrakech and Tamuda Bay. Marriott's Morocco portfolio spans all segments from upper upscale business hotels in Casablanca and Rabat to luxury resort developments on the Atlantic and Mediterranean coasts.",
  'Hyatt Hotels Corporation': "Hyatt Hotels Corporation is a leading global hospitality company headquartered in Chicago, with a portfolio of over 20 brands across luxury, lifestyle, and select-service segments. In Morocco, Hyatt operates through Hyatt Regency, Park Hyatt, and Hyatt Place, with properties in Casablanca and the Taghazout Bay resort destination. The group entered Morocco in 1973 with the opening of Hyatt Regency Casablanca, one of the country's first international luxury hotel brands, and has since expanded into the emerging resort corridor of Agadir and Taghazout. Hyatt's Morocco strategy focuses on premium resort and urban business hotels targeting international corporate and leisure travelers.",
  'Accor': "Accor is Europe's largest hotel group and Morocco's dominant hospitality operator, with a portfolio spanning ultra-luxury to economy through brands including Sofitel, Fairmont, Pullman, Mövenpick, Novotel, Mercure, Ibis, and MGallery. In Morocco, Accor operates primarily through Risma, its listed subsidiary on the Casablanca Stock Exchange and the country's only publicly traded hotel company. Having been present in Morocco for over 50 years, Accor manages the largest branded hotel portfolio in the country by both number of properties and total keys. The group's footprint covers all major destinations from Casablanca and Marrakech to Agadir, Fes, Rabat, and Tanger, with continued expansion through new lifestyle brands including Mama Shelter and 25hours.",
  'Four Seasons Hotels & Resorts': "Four Seasons Hotels & Resorts is a Canadian luxury hospitality company operating over 120 properties in 50 countries, consistently ranked among the world's finest hotel brands. In Morocco, Four Seasons has established a significant presence with landmark properties in Casablanca, Marrakech, and the newly opened Rabat at Kasr Al Bahr, reflecting the brand's confidence in Morocco's luxury tourism potential. Each Four Seasons property in Morocco is positioned at the very top of its local market, offering bespoke service standards and prime real estate locations that set the benchmark for ultra-luxury hospitality in the country. The brand's continued investment in Morocco aligns with the kingdom's Vision 2030 tourism ambitions and the growing appetite from high-net-worth international travelers.",
  'Radisson Hotel Group': "Radisson Hotel Group is a Belgian-based multinational hospitality company operating over 1,700 hotels across 120 countries through brands including Radisson Blu, Radisson, Radisson RED, and Park Inn. In Morocco, Radisson has emerged as one of the most active international operators, with a rapidly expanding portfolio spanning Casablanca, Marrakech, Al Hoceima, Saidia, and the Taghazout Bay resort corridor. The group's Morocco strategy combines full-service Radisson Blu properties in major urban and resort destinations with the newer Radisson Residences concept targeting the branded residential segment. Radisson's aggressive expansion in Morocco reflects its broader Africa and Middle East growth strategy and its early recognition of Morocco's emerging status as a premium tourism and investment destination.",
  'RIU Hotels & Resorts': "RIU Hotels & Resorts is a Spanish family-owned hotel group founded in 1953 and one of Europe's leading all-inclusive resort operators, with over 100 properties across 20 countries. In Morocco, RIU has built the country's largest beach resort portfolio with six properties concentrated in Agadir and Marrakech, representing a significant share of Morocco's international leisure tourism capacity. The group's Tikida brand operates a cluster of all-inclusive resorts in Agadir that have been foundational to the city's development as a mass-market European beach destination, while the newer Riu Palace Tikida Taghazout positions the group in the premium resort segment. RIU's long-standing commitment to Morocco and its large room count make it one of the most influential operators in the country's leisure tourism ecosystem.",
  'Hilton Hotels & Resorts': "Hilton Hotels & Resorts is one of the world's most recognized hospitality brands, part of the Hilton portfolio of 22 brands operating over 7,000 properties across 123 countries. In Morocco, Hilton has built a diversified portfolio spanning its full-service Hilton brand, Hilton Garden Inn, DoubleTree, Conrad, and the ultra-luxury Waldorf Astoria, with properties across Casablanca, Tanger, Rabat, and the Taghazout Bay resort destination. The group's Morocco expansion has accelerated significantly in recent years, with major openings in Tanger and the Taghazout Bay surf village reinforcing Hilton's commitment to the country's growing tourism infrastructure. The recently opened Waldorf Astoria Rabat Salé represents Hilton's most prestigious Morocco asset and signals the group's confidence in the capital's luxury hospitality potential.",
  'Barceló Hotel Group': "Barceló Hotel Group is a Spanish family-owned hospitality company founded in 1931, operating over 270 hotels across 24 countries through brands including Barceló Hotels, Royal Hideaway, and Occidental. In Morocco, Barceló has assembled one of the largest international operator portfolios in the country with properties spanning Casablanca, Fes, and Tanger, reflecting the group's long-standing strategic interest in the Moroccan market. The group's flagship Royal Hideaway Casablanca positions Barceló at the top of the luxury segment in the economic capital, while the recently rebranded Hotel Borj Rabat expands its presence into the administrative capital. Barceló's deep roots in Spanish-speaking markets and its established relationships with European tour operators make it a natural bridge between Morocco's traditional European feeder markets and its growing international ambitions.",
  'Kenzi Hotels Group': "Kenzi Hotels Group is Morocco's largest home-grown hotel chain, with a portfolio of upper upscale and luxury properties operating exclusively within the kingdom. Founded in the 1970s and headquartered in Casablanca, Kenzi has built an iconic presence in Morocco's key destinations including Casablanca, Marrakech, Tanger, and Ouarzazate, with properties that have defined the upper upscale segment in their respective markets for decades. The Kenzi Tower Hotel in Casablanca and the Kenzi Menara Palace in Marrakech are among the most recognized hotel addresses in Morocco, serving a loyal base of domestic corporate clients and international leisure travelers. As one of the few large-scale independent Moroccan hotel groups, Kenzi represents an important counterweight to international brands and a significant part of the country's hospitality heritage.",
  'Club Med': "Club Med is a French pioneering all-inclusive resort company founded in 1950, credited with creating the modern all-inclusive holiday concept and operating over 70 resorts across 26 countries. In Morocco, Club Med has a historic presence dating back to 1966 with the opening of Club Med Marrakech La Palmeraie, one of the group's earliest properties globally, followed by Club Med Yasmina on the Mediterranean coast at Cabo Negro, near M'diq and Tétouan. The two Moroccan resorts serve primarily European leisure travelers seeking a premium all-inclusive experience in culturally rich destinations, contributing meaningfully to Morocco's international leisure tourism arrivals. Club Med's long relationship with Morocco reflects the country's enduring appeal as a European holiday destination and its unique positioning at the intersection of European comfort and North African cultural immersion.",
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
  'Relais & Châteaux': "Relais & Châteaux is a French association of independently owned luxury hotels and restaurants founded in 1954, uniting over 580 properties across 60 countries under a shared commitment to exceptional gastronomy, architectural heritage, and personalised hospitality. In Morocco, Relais & Châteaux is represented by six distinctive properties spanning Fes, Essaouira, Casablanca, Meknès, Marrakech, and Dakhla — making it one of the most geographically diverse luxury collections in the kingdom. Each Moroccan member of the collection exemplifies the association's core values of intimacy, authenticity, and deep rootedness in its cultural and architectural context, from the medina riads of Fes to the Atlantic wind resort of Dakhla. Morocco's Relais & Châteaux properties are among the most celebrated boutique luxury addresses in North Africa and represent a pinnacle of the country's independent luxury hospitality tradition.",
  'Wyndham Hotels & Resorts': "Wyndham Hotels & Resorts is the world's largest hotel franchising company by number of properties, operating over 9,000 hotels across 95 countries through a portfolio of 24 brands spanning economy to upper upscale segments. In Morocco, Wyndham's presence is represented through the Ramada Encore by Wyndham brand in Tanger, targeting the upper midscale and upscale business and leisure traveler segment in one of Morocco's fastest-growing hotel markets. The group's selective approach to Morocco reflects a broader strategy of using franchise partnerships to establish a foothold in emerging markets before expanding through additional brand tiers. Wyndham's global loyalty program and distribution network provide its Morocco property with connectivity to a vast base of international travelers that would otherwise be difficult to reach through independent channels.",
  'Louvre Hotels Group': "Louvre Hotels Group is a French hospitality company and one of Europe's largest hotel groups, operating over 1,500 hotels across 54 countries through brands including Golden Tulip, Tulip Inn, and Royal Tulip. In Morocco, Louvre Hotels Group is represented by the Royal Tulip City Center Tanger, an upper upscale property in the heart of Morocco's northern commercial hub. The Royal Tulip brand targets the upper upscale business and leisure segment with a focus on full-service amenities and prime city center locations, making Tanger a natural fit given the city's growing importance as a regional business and logistics hub. Louvre Hotels Group's presence in Morocco reflects the country's attractiveness to mid-to-large European hotel groups seeking to establish footholds in North Africa's most accessible and stable tourism market.",
  'Groupe Barrière': "Groupe Barrière is a French family-owned luxury hospitality and entertainment company founded in 1912, operating a portfolio of prestigious hotels, casinos, and spas primarily in France and internationally. In Morocco, Groupe Barrière is represented by the Barrière Naroua Marrakech, a luxury property opened in 2023 that brings the group's signature blend of refined French hospitality traditions and contemporary lifestyle experiences to one of the world's most celebrated leisure destinations. The Naroua marks Barrière's first African property and reflects the group's ambition to selectively expand its luxury hotel portfolio beyond its traditional European strongholds into destinations that attract the cosmopolitan high-net-worth travelers it serves. Groupe Barrière's entry into Marrakech adds a distinctly French luxury sensibility to a city already renowned for its concentration of world-class hospitality experiences.",
  'Groupe Lucien Barrière': "Groupe Barrière is a French family-owned luxury hospitality and entertainment company founded in 1912, operating a portfolio of prestigious hotels, casinos, and spas primarily in France and internationally. In Morocco, Groupe Barrière is represented by the Barrière Naroua Marrakech, a luxury property opened in 2023 that brings the group's signature blend of refined French hospitality traditions and contemporary lifestyle experiences to one of the world's most celebrated leisure destinations. The Naroua marks Barrière's first African property and reflects the group's ambition to selectively expand its luxury hotel portfolio beyond its traditional European strongholds into destinations that attract the cosmopolitan high-net-worth travelers it serves. Groupe Barrière's entry into Marrakech adds a distinctly French luxury sensibility to a city already renowned for its concentration of world-class hospitality experiences.",
  'Virgin Limited Edition': "Virgin Limited Edition is the ultra-luxury hotel collection of Sir Richard Branson's Virgin Group, operating a small portfolio of extraordinary private island and wilderness retreats that emphasize exclusivity, sustainability, and transformative guest experiences. In Morocco, Virgin Limited Edition's single property is Kasbah Tamadot in the High Atlas Mountains near Marrakech, a stunning converted kasbah offering 28 rooms and suites with panoramic mountain views that has become one of Morocco's most iconic luxury retreats since its opening. The property embodies the Virgin Limited Edition philosophy of placing guests in remarkable natural and cultural settings with highly personalised service and a strong commitment to supporting local communities and environmental conservation. Kasbah Tamadot's presence in Morocco adds a dimension of adventure-tinged luxury to the country's hotel offer that few other properties can match.",
  'Globalia Hotels': "Globalia Hotels is the hotel division of Globalia, one of Spain's largest travel and tourism conglomerates, operating the Be Live brand across popular Mediterranean, Caribbean, and North African leisure destinations. In Morocco, Globalia's Be Live brand is represented by Be Live Saidia in the Mediterrania Saidia resort complex and by Be Live Collection Marrakech (adults only). Be Live Saidia targets the all-inclusive European package travel segment that forms the backbone of Saidia's hotel market. The property serves primarily Spanish and European charter travelers seeking a cost-effective all-inclusive beach holiday experience in Morocco's northeastern Mediterranean resort corridor. Globalia's presence in Saidia reflects the strong historical ties between Spanish tour operators and Morocco's northern coastal resort destinations and the continued importance of the all-inclusive format for European mass-market leisure tourism in Morocco.",
  'Banyan Tree': "Banyan Tree Hotels & Resorts is a Singapore-based luxury hospitality company founded in 1994, renowned for pioneering the private pool villa concept and operating a portfolio of award-winning luxury resorts, spas, and residences across Asia, the Middle East, Africa, and the Americas. In Morocco, Banyan Tree operates a single ultra-luxury property in Tamuda Bay, the Banyan Tree Tamuda Bay, bringing the brand's signature blend of intimate seclusion, world-class spa philosophy, and deep environmental sensitivity to Morocco's emerging Mediterranean luxury corridor. The property's presence in Tamuda Bay reflects Banyan Tree's deliberate strategy of establishing footholds in destinations at the early stages of luxury development, positioning the brand ahead of the wave of international interest that follows. Banyan Tree Tamuda Bay adds an Asian luxury sensibility to a destination already attracting significant international brand investment.",
  'Vichy Thermalia': "Vichy Thermalia is a French thermal wellness hospitality brand operated under the Vichy Célestins Spa Hotels network, specializing in medically supervised thermal spa hotels that combine hydrotherapy treatments with premium hotel accommodation in destinations with natural mineral water sources. In Morocco, Vichy Thermalia operates the Vichy Thermalia Spa Hotel in Moulay Yacoub, a thermal resort town located 20 kilometers northwest of Fes renowned for its natural hot springs and longstanding reputation as a wellness destination. The property is developed in partnership with Madaëf and represents Morocco's most sophisticated medically oriented thermal spa offering, targeting both domestic wellness travelers and international guests seeking therapeutic spa experiences in a culturally rich environment. Vichy Thermalia's presence in Moulay Yacoub reinforces Morocco's ambition to develop its natural thermal assets into internationally competitive wellness tourism destinations.",
  'Valeria Hotels': "Valeria Hotels is a Moroccan independent hotel group specializing in large-scale club resort properties targeting the European all-inclusive leisure market. Operating exclusively within Morocco, Valeria has built a significant resort portfolio concentrated in Marrakech's Palmeraie district and Agadir, with properties that combine extensive leisure facilities, entertainment programming, and all-inclusive packages tailored to family and group travelers. The group's Marrakech properties in the Palmeraie have established Valeria as one of the largest resort operators in the city's leisure segment, while the Agadir property serves the Atlantic coast's strong European charter market. Valeria's most recent addition, the Valeria Kasbah del Mar in Cabo Negro on the Mediterranean coast, signals the group's ambition to expand into Morocco's emerging northern resort corridor.",
  'Pickalbatros': "Pickalbatros is an Egyptian hospitality group operating a portfolio of upscale and upper upscale all-inclusive resorts across North Africa and the Middle East, with a growing presence in Morocco. The group's Morocco portfolio is concentrated in Marrakech and Agadir, where it operates six large-scale resort properties ranging from family-oriented all-inclusive clubs to adults-only beachfront resorts and golf properties. Pickalbatros targets the European and regional leisure travel market with a consistent all-inclusive product offering that combines extensive amenities, entertainment programming, and prime resort locations. The group's expansion into Morocco reflects its confidence in the country's growing appeal as a year-round leisure destination for European and Middle Eastern travelers.",
};

function getBrandLogoUrl(brandGroup) {
  const domain = BRAND_DOMAINS[brandGroup];
  if (!domain) return null;
  return `https://cdn.brandfetch.io/domain/${domain}?c=1idptYpdMe9b8BdTIPC`;
}

function getBrandLogoImg(brandGroup, size=24, fallbackHtml='') {
  const fallback = fallbackHtml || brandInitials(brandGroup, size, 6);
  const localLogo = LOCAL_BRAND_LOGOS[brandGroup];
  if (localLogo) return logoChipImg(localLogo, brandGroup, size, 6, fallback);
  const custom = BRAND_CUSTOM_LOGOS[brandGroup];
  if (custom) return initialsTile(custom.letter, size, 6, custom.bg, custom.color);
  const domain = BRAND_DOMAINS[brandGroup];
  if (!domain) return brandGroup ? fallback : '';
  return logoChipImg('https://cdn.brandfetch.io/domain/' + domain + '?c=1idptYpdMe9b8BdTIPC', brandGroup, size, 6, fallback);
}

// Segment colours for charts/dots follow the segment label families (see SEGMENT_FAMILY)
const SEG_COLORS = new Proxy({}, { get: (_, seg) => familyDot(SEGMENT_FAMILY[seg] || 'grey') });

// Grayscale tier hierarchy (Notion-style monochrome base) — higher tiers
// read slightly more prominent, lowest tier most muted. Orange is kept
// off descriptive segment badges entirely since these label a fixed
// property attribute rather than an interactive/selected state; theme-
// aware because a fixed white-tint background (dark-mode-only) would be
// invisible against a light-mode white surface.
function getSegmentBadgeHtml(segment) {
  if (!segment) return '—';
  return `<span class="segment-badge pill--${SEGMENT_FAMILY[segment] || 'grey'}">${fmt.esc(segment).toUpperCase()}</span>`;
}

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
// Google Maps styles from the palette (static/js/palette.js). Neutrals are hex
// in both modes, which the Maps style API requires.
function gmapStyles() {
  const p = KodoPalette.get();
  const water = p.theme === 'dark' ? p.bg : p.families.blue.tint;
  return [
    { elementType: 'geometry', stylers: [{ color: p.bgAlt }] },
    { elementType: 'labels.text.fill', stylers: [{ color: p.text2 }] },
    { elementType: 'labels.text.stroke', stylers: [{ color: p.bgAlt }] },
    { featureType: 'administrative', elementType: 'geometry', stylers: [{ color: p.border }] },
    { featureType: 'administrative.country', elementType: 'geometry.stroke', stylers: [{ color: p.text3 }] },
    { featureType: 'administrative.country', elementType: 'labels.text.fill', stylers: [{ color: p.text }] },
    { featureType: 'administrative.province', elementType: 'geometry.stroke', stylers: [{ color: p.border }] },
    { featureType: 'administrative.locality', elementType: 'labels.text.fill', stylers: [{ color: p.text2 }] },
    { featureType: 'poi', stylers: [{ visibility: 'off' }] },
    { featureType: 'transit', stylers: [{ visibility: 'off' }] },
    { featureType: 'road', elementType: 'geometry', stylers: [{ color: p.bg }] },
    { featureType: 'road', elementType: 'geometry.stroke', stylers: [{ color: p.border }] },
    { featureType: 'road.highway', elementType: 'geometry', stylers: [{ color: p.border }] },
    { featureType: 'water', elementType: 'geometry', stylers: [{ color: water }] },
  ];
}


// Year-on-year change pills for the dashboard KPI cards. Empty: the old
// values (+6.2% YoY and so on) were fixed numbers with no prior-year data
// behind them. Fill in from real data when a comparison period exists.
const KPI_DELTAS = {};

Chart.register(ChartDataLabels);

// Global: no grid lines, tick marks or axis borders on any chart
Chart.defaults.scale.grid.display   = false;
Chart.defaults.scale.grid.drawTicks = false;
Chart.defaults.scale.border.display = false;
// Default text and (if ever shown) grid colours follow the palette and the theme
Chart.defaults.color = KodoPalette.get().text2;
Chart.defaults.scale.grid.color = KodoPalette.get().grid;
KodoPalette.onChange(p => { Chart.defaults.color = p.text2; Chart.defaults.scale.grid.color = p.grid; });
Chart.defaults.font.family = "'Sweet Sans Pro', sans-serif";
Chart.defaults.scales.linear.ticks.font = { weight: '400', family: "'Sweet Sans Pro', sans-serif" };

// ─── State & cache ────────────────────────────────────────────────

const state = {
  city:    'all',
  mapSeg:  'all',
  tab:     'overview',   // one destination: overview | hotels | brands (remembered)
  destMetric: 'bar',     // the number next to each destination in the sidebar: bar | occ
};

let apiData  = null;   // /api/data response
let hotels   = null;   // /api/hotels response (flat, merged)
let googleMap          = null;
let googlePipelineMap  = null;
let googleMapsApiReady = false;
let hotelMarkers       = [];   // one marker per city: [{marker, city, hotels, count}]
let pipelineMarkers    = [];   // [{marker, project}]
let activeInfoWindow   = null;
let brandChart      = null;
let brandHotelsData = [];
const brandState    = { col: 'name', dir: 1 };
let activeBrandCity = null;
const BRAND_STR_COLS = new Set(['name', 'city', 'category', 'owner', 'status']);
let brandDetailGroup = null;
let tourismInited   = false;
let pipelineInited  = false;
let pipelineData    = null;
const pipelineState = { stage: 'all', city: 'all', group: 'all', q: '', view: 'table' };
const pipelineSort  = { col: 'expected_opening', dir: 1 };

let hotelDetailPrevScreen = 'hotels';
let hotelCityChart        = null;

let brandsData   = null;
let brandsInited = false;
let brandDetailPrevScreen = 'dashboard';
const brandsFilter   = { sort: 'total_keys', dir: -1, search: '', segment: 'all' };
const BRANDS_STR_COLS = new Set(['brand_group']);
// Brand share colours cycle through the chart series (blue, green, orange, violet, sky, grey)
const BRAND_PALETTE = new Proxy([], { get: (_, i) => (i === 'length' ? 6 : KodoPalette.get().series[Number(i) % 6]) });

// ─── Theme ────────────────────────────────────────────────────────

function applyTheme(mode) {
  if (mode === 'light') {
    document.body.classList.add('light');
  } else {
    document.body.classList.remove('light');
  }
  document.querySelectorAll('#theme-toggle .mk-toggle-opt').forEach(opt => {
    opt.classList.toggle('mk-toggle-active', opt.dataset.val === mode);
  });
  swapMapTheme(mode);
}

document.querySelectorAll('#theme-toggle .mk-toggle-opt').forEach(opt => {
  opt.addEventListener('click', () => {
    const next = opt.dataset.val;
    if (KodoTheme.get() === next) return;
    KodoTheme.set(next);
    applyTheme(next);
    redrawChartsForTheme();
  });
});

applyTheme(KodoTheme.get());

// ─── Loading state ──────────────────────────────────────────────────

function showLoading(container) {
  if (!container) return;
  container.innerHTML = `
    <div style="padding:40px 0;">
      <div class="kodo-loader"></div>
      <div class="kodo-loader-text">LOADING</div>
    </div>
  `;
}

// ─── Empty state ────────────────────────────────────────────────────

function getEmptyStateHtml(message, subtext) {
  return `
    <div class="kodo-empty">
      <span class="kodo-empty-msg">[ NO DATA ]</span>
      <span class="kodo-empty-sub">${fmt.esc(message || 'No results found')}</span>
      ${subtext ? `<span class="kodo-empty-hint">${fmt.esc(subtext)}</span>` : ''}
    </div>
  `;
}

// ─── Formatters ───────────────────────────────────────────────────

// A missing figure (null, e.g. a hotel added without an FY estimate) shows as "—", never 0
const _missing = v => v == null || v === '' || Number.isNaN(Number(v));
const fmt = {
  pct: v  => _missing(v) ? '—' : (v * 100).toFixed(1) + '%',
  num: v  => _missing(v) ? '—' : Math.round(v).toLocaleString('en'),
  mad: v  => _missing(v) ? '—' : Math.round(v).toLocaleString('en'),
  esc: s  => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'),
};

// ─── Period labels ────────────────────────────────────────────────
// One wording for "which period does this figure cover, and when was it
// last updated", used by every KPI card and Excel export. period_label() /
// period_caption() in utils.py write the same strings into the PDF report;
// keep the two in step.
//
// Headline cards show the period the data covers: BAR since 3 November
// 2026 (KodoBar), Kodo estimates for the next 30 nights (KodoLive), a
// snapshot as of today for counts.
//   {kind:'fy', year:2026}                      → FY 2026
//   {kind:'year', year:2025}                    → 2025          (calendar year)
//   {kind:'month', year:2026, month:9}          → Sep 2026
//   {kind:'ltm', year:2026, month:9}            → Last 12 months to Sep 2026
//   {kind:'season', season:'Summer', year:2026} → Summer 2026
//   {kind:'days', days:30}                      → Last 30 days   (ending today or yesterday)
//   {kind:'window', days:30, end:'2026-06-01'}  → 30 days to 1 Jun 2026   (an older window)
//   {kind:'range', start:'2026-03-04', end:'2026-06-01'} → 4 Mar – 1 Jun 2026
//   {kind:'asof', date:Date|'YYYY-MM-DD'}       → As of 28 Oct 2026
//   {kind:'forecast', year:2026}                → 2026 forecast
//   {kind:'sample'}                             → Sample data · illustrative figures (never a date)
//   {kind:'next', days:30}                      → Next 30 days   (forward-looking: published rates)
const KodoPeriod = (() => {
  const MON = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const toDate = d => d instanceof Date ? d : new Date(String(d).slice(0, 10) + 'T00:00:00');
  const day = (d, withYear = true) => {
    d = toDate(d);
    return `${d.getDate()} ${MON[d.getMonth()]}` + (withYear ? ` ${d.getFullYear()}` : '');
  };
  function label(p) {
    if (!p) return '';
    switch (p.kind) {
      case 'fy':       return `FY ${p.year}`;
      case 'year':     return String(p.year);
      case 'month':    return `${MON[p.month - 1]} ${p.year}`;
      case 'ltm':      return `Last 12 months to ${MON[p.month - 1]} ${p.year}`;
      case 'season':   return `${p.season} ${p.year}`;
      case 'days':     return `Last ${p.days} days`;
      case 'window':   return `${p.days} days to ${day(p.end)}`;
      case 'range': {
        const sameYear = toDate(p.start).getFullYear() === toDate(p.end).getFullYear();
        return `${day(p.start, !sameYear)} – ${day(p.end)}`;
      }
      case 'asof':     return `As of ${day(p.date)}`;
      case 'forecast': return `${p.year} forecast`;
      case 'multi':    return p.parts.map(label).join(' / ');
      case 'sample':   return 'Sample data · illustrative figures';
      case 'next':     return `Next ${p.days} days`;
    }
    return '';
  }
  // Period codes as stored in the data files: a fiscal year, '2026', '2026-09'
  function fromData(code) {
    const s = String(code || '').trim();
    let m;
    if ((m = s.match(/^(\d{4})\s*FY$/i)) || (m = s.match(/^FY\s*(\d{4})$/i))) return { kind: 'fy', year: +m[1] };
    if ((m = s.match(/^(\d{4})E$/i))) return { kind: 'forecast', year: +m[1] };
    if ((m = s.match(/^(\d{4})$/))) return { kind: 'year', year: +m[1] };
    if ((m = s.match(/^(\d{4})-(\d{2})$/))) return { kind: 'month', year: +m[1], month: +m[2] };
    return null;
  }
  // Tooltip: data source, plus the last update date when the data has one
  function tip({ source, updated, note } = {}) {
    return [source && `Source: ${source}`, updated && `Last updated ${day(updated)}`, note]
      .filter(Boolean).join(' · ');
  }
  // "Last 30 days · vs comp set, same dates · updated 29 Oct 2026"
  function caption(p, { compare, updated } = {}) {
    const l = label(p);
    return l ? [l, compare, updated && `updated ${day(updated)}`].filter(Boolean).join(' · ') : '';
  }

  function periodEl(card) {
    let el = card.querySelector('.kpi-period');
    if (!el) {
      el = document.createElement('span');
      el.className = 'kpi-period';
      const anchor = card.querySelector('.kpi-label, .bench-kpi-title');
      if (anchor) anchor.after(el); else card.prepend(el);
    }
    return el;
  }
  // Write the period line into a KPI card, directly under its label: the
  // period, what the figure is compared against, and the update date (opts
  // {compare, updated}; a string is taken as compare). With no period (not
  // determinable from the data) the line stays blank so the values in a
  // row still line up.
  function set(card, p, tipText, opts) {
    if (typeof card === 'string') card = document.getElementById(card);
    if (!card) return;
    const el = periodEl(card);
    const text = caption(p, typeof opts === 'string' ? { compare: opts } : (opts || {}));
    el.textContent = text || ' ';
    el.classList.toggle('kpi-period--none', !text);
    if (text && tipText) el.title = tipText; else el.removeAttribute('title');
    if (text) el.removeAttribute('aria-hidden'); else el.setAttribute('aria-hidden', 'true');
  }
  // A free text period line (live cards: "5 Nov – 4 Dec 2026 · updated 4 Nov 03:20")
  function setText(card, text, tipText) {
    if (typeof card === 'string') card = document.getElementById(card);
    if (!card) return;
    const el = periodEl(card);
    el.textContent = text || ' ';
    el.classList.toggle('kpi-period--none', !text);
    if (text && tipText) el.title = tipText; else el.removeAttribute('title');
    if (text) el.removeAttribute('aria-hidden'); else el.setAttribute('aria-hidden', 'true');
  }
  return { label, caption, vs: p => p ? 'vs ' + label(p) : '', fromData, tip, set, setText, day,
           date: day, today: () => ({ kind: 'asof', date: new Date() }) };
})();

// ─── Live KPI cards (/api/live-kpis, live_kpis.py) ────────────────────
// One set of figures for every page: each hotel's average published rate
// (latest price per night), modelled occupancy and indicative Rooms RevPAR over
// the next 30 nights; a group (city, brand, owner, market) is the rooms-
// weighted average over its hotels that have the figure, with the
// coverage shown. Published booking-site prices (BAR); modelled, not
// measured occupancy. The 7-day change only once that snapshot exists.
// Flags for changes to figures clients see (flags.py; window.KODO_FLAGS from
// the page). All off until approved: with a flag off, nothing changes.
const KODO_FLAG = name => !!(window.KODO_FLAGS && window.KODO_FLAGS[name]);

// ─── BAR (published rate) since 3 November 2026 ───────────────────
// The one observed rate figure. A hotel's BAR is its average over the
// nights since 3 November 2026 (the last published price seen before each
// night), from 7 priced nights (bar_mad, bar_nights in /api/hotels and
// /api/live-kpis). A group's BAR (destination, brand, owner, segment) is the
// median of its hotels' BAR; under 3 such hotels it reads "Limited
// data", never a precise-looking number. Kodo has no achieved rate, so
// this is always called BAR or published rate. Occupancy and Rooms RevPAR are Kodo estimates (next 30 nights).
const KodoBar = (() => {
  const COLLECTING = 'Collecting data since 3 November';
  const LIMITED = 'Limited data';
  let meta = { since: '2026-11-03', days: 0, min_nights: 7, min_hotels: 3 };
  const setMeta = m => { if (m) meta = { ...meta, ...m }; };
  const longDay = iso => new Date(String(iso).slice(0, 10) + 'T00:00:00')
    .toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });
  const since = () => `Since ${longDay(meta.since)}`;
  const days = () => `${meta.days} day${meta.days === 1 ? '' : 's'} of data`;
  const caption = () => `${since()} · ${days()}`;
  // list: rows with bar_mad and bar_nights -> {val, n, nights, limited}
  function group(list) {
    const ok = (list || []).filter(h => h && h.bar_mad != null && !Number.isNaN(Number(h.bar_mad)));
    // the median of the hotels' BAR: one hotel's suite-level price can't move a city
    const vs = ok.map(h => Number(h.bar_mad)).sort((a, b) => a - b), m = vs.length >> 1;
    const val = vs.length ? (vs.length % 2 ? vs[m] : (vs[m - 1] + vs[m]) / 2) : null;
    return { val, n: ok.length, nights: ok.reduce((t, h) => t + (Number(h.bar_nights) || 0), 0),
             limited: ok.length < meta.min_hotels };
  }
  const shown = g => g && g.val != null && !g.limited;
  // A table cell: the figure, "Limited data" or "—", with what it rests on
  function cell(g) {
    if (!g || g.val == null) return `<span class="bar-na" title="No hotel with ${meta.min_nights} priced nights yet">—</span>`;
    const tip = `BAR (published rate) · ${caption()} · ${g.n} hotel${g.n === 1 ? '' : 's'}, ${g.nights} nights`;
    return g.limited ? `<span class="bar-limited" title="${tip}">${LIMITED.toLowerCase()}</span>`
      : `<span title="${tip}">${fmt.mad(g.val)}</span>`;
  }
  // One hotel's BAR in a table: the figure, or "—" under 7 priced nights
  function hotelCell(h) {
    if (h.bar_mad == null) return `<span class="bar-na" title="${h.bar_nights || 0} priced night${h.bar_nights === 1 ? '' : 's'} since 3 November: needs ${meta.min_nights}">—</span>`;
    return `<span title="BAR (published rate) · ${caption()} · ${h.bar_nights} nights">${fmt.mad(h.bar_mad)}</span>`;
  }
  // The KPI card. g: a group ({val, n, nights, limited}) or one hotel ({single, val, nights})
  function card(c, g, d) {
    const L = KodoLive;
    c.querySelector('.kpi-label').textContent = 'BAR (published rate)';
    if (d) setMeta({ since: d.bar_since, days: d.bar_days, min_nights: d.min_bar_nights, min_hotels: d.min_bar_hotels });
    // Past stay nights only: from 3 Nov to today, each night at the last price seen before it
    KodoPeriod.setText(c, `Past nights since ${longDay(meta.since).replace(/ \d{4}$/, '')}, up to today · ${days()}`,
      KodoPeriod.tip({ source: 'published hotel rates, the last price seen before each night', note: 'observed; the public price, not what guests paid' }));
    const v = c.querySelector('.kpi-value');
    v.classList.remove('kpi-value--limited');
    const d0 = c.querySelector('.kpi-delta'); if (d0) { d0.textContent = ''; d0.style.display = 'none'; }
    if (g.single) {
      if (g.val == null) { L.noData(c, g.nights ? LIMITED : COLLECTING); L.part(c, 'kpi-sub').textContent = `${g.nights} priced night${g.nights === 1 ? '' : 's'}: needs ${meta.min_nights}`; return; }
      L.show(c, fmt.mad(g.val), 'MAD'); L.part(c, 'kpi-sub').textContent = `average of ${g.nights} nights`; return;
    }
    if (g.val == null) { L.noData(c, COLLECTING); L.part(c, 'kpi-sub').textContent = `no hotel with ${meta.min_nights} priced nights yet`; return; }
    if (g.limited) { L.noData(c, LIMITED); L.part(c, 'kpi-sub').textContent = `${g.n} hotel${g.n === 1 ? '' : 's'} with ${meta.min_nights} priced nights: needs ${meta.min_hotels}`; return; }
    L.show(c, fmt.mad(g.val), 'MAD'); L.part(c, 'kpi-sub').textContent = `median of ${g.n} hotels' average BAR · ${g.nights.toLocaleString('en')} priced nights`;
  }
  // The empty state of a chart or card with no real data yet
  const collecting = (detail = '') => `<div class="collecting-state" role="status"><span class="collecting-dot" aria-hidden="true"></span>`
    + `<span class="collecting-title">${COLLECTING}</span>${detail ? `<span class="collecting-sub">${detail}</span>` : ''}</div>`;
  return { COLLECTING, LIMITED, setMeta, since, days, caption, group, shown, cell, hotelCell, card, collecting,
           meta: () => meta };
})();
const ROOMS_REVPAR_TIP = 'Rooms RevPAR is room revenue per available room. It excludes food and beverage and other revenue. On Kodo it is estimated from modelled occupancy and the published rate (BAR).';
const EST_TIP = 'Kodo estimate: occupancy model, next 30 nights; Rooms RevPAR = BAR × modelled occupancy. ' + ROOMS_REVPAR_TIP;
// Where the hotel's city is held to its official monthly occupancy (occ_calibrated / calibrated from the APIs)
const CALIBRATED_LABEL = 'Kodo est., calibrated on official monthly city occupancy';
// A hotel under renovation but partly open (hotel_flags.json): its prices and BAR
// as usual, no occupancy estimate, its rooms out of the totals
const RENOVATION_LABEL = 'Partly open, under renovation: no occupancy estimate';
// A hotel closed for the season over the coming 30 nights (hotel_flags.json closed_months):
// no occupancy or Rooms RevPAR, its rooms out of the totals
const CLOSED_LABEL = 'Closed for the season';
const CLOSED_NOTE = 'Usually closed in winter';
const hotelRooms = h => h.under_renovation ? `${fmt.num(h.keys_listed)} (partly open, under renovation)`
  : h.seasonal_closure ? `${fmt.num(h.keys_listed)} (${CLOSED_NOTE.toLowerCase()})` : fmt.num(h.keys);
const hotelOcc = h => h.under_renovation ? RENOVATION_LABEL : h.seasonal_closure ? CLOSED_LABEL : fmt.pct(h.occupancy);
const COUNT_TIP = KodoPeriod.tip({ source: 'Kodo hotel database', note: 'count when this page loaded' });

const KodoLive = (() => {
  let data = null, loading = null;
  function load() {
    if (data) return Promise.resolve(data);
    if (!loading) loading = fetch('/api/live-kpis').then(r => r.ok ? r.json() : null).catch(() => null)
      .then(d => { data = d; loading = null; return d; });
    return loading;
  }
  // list: hotels ({id, keys}); returns the rooms-weighted figures and coverage
  // Confidence of a group of hotels (data_quality.group_level): medium or
  // better on 60% of the rooms -> medium (high if 60% are high), else low
  // when 30% are at least low, else insufficient. null before the checks ran.
  const LEVELS = ['insufficient', 'low', 'medium', 'high'];
  function groupLevel(rows) {
    let tot = 0, known = 0, good = 0, some = 0, high = 0;
    rows.forEach(v => {
      if (!v.keys) return;
      tot += v.keys;
      const i = LEVELS.indexOf(v.confidence);
      if (i < 0) return;
      known += v.keys;
      if (i >= 2) good += v.keys;
      if (i >= 1) some += v.keys;
      if (i === 3) high += v.keys;
    });
    if (!tot || !known) return null;
    if (good / tot >= 0.6) return high / tot >= 0.6 ? 'high' : 'medium';
    return (some / tot >= 0.3 || good / tot >= 0.3) ? 'low' : 'insufficient';
  }
  function agg(list) {
    const H = (data && data.hotels) || {};
    const rows = (list || []).map(h => H[String(h.id)]).filter(Boolean);
    const w = sel => {
      let num = 0, den = 0, n = 0;
      rows.forEach(v => { const x = sel(v); if (x != null && v.keys) { num += x * v.keys; den += v.keys; n++; } });
      return den ? { val: num / den, n } : { val: null, n: 0 };
    };
    const change = sel => {
      if (!data || !data.change_from) return null;
      let a = 0, b = 0, den = 0;
      rows.forEach(v => { const x = sel(v), y = v.prev && sel(v.prev); if (x != null && y != null && v.keys) { a += x * v.keys; b += y * v.keys; den += v.keys; } });
      return den ? { now: a / den, then: b / den } : null;
    };
    return {
      total: (list || []).length, single: (list || []).length === 1 ? rows[0] || null : null, level: groupLevel(rows),
      bar: KodoBar.group(rows.map(v => ({ bar_mad: v.bar, bar_nights: v.bar_nights }))),
      rate: w(v => v.rate), occ: w(v => v.occ), low: w(v => v.occ_low), high: w(v => v.occ_high), revpar: w(v => v.revpar),
      rlow: w(v => v.revpar_low), rhigh: w(v => v.revpar_high),
      calibrated: rows.length > 0 && rows.every(v => v.occ_calibrated),
      // destination levels (Saidia, Nador, Al Hoceima): how many real hotels the estimate rests on
      basis: (() => { const b = rows.filter(v => v.occ_basis && v.occ != null); if (!b.length) return '';
        const texts = [...new Set(b.map(v => v.occ_basis))], all = rows.filter(v => v.occ != null).length;
        return (b.length < all ? `${b.length} of ${all} hotels: ` : '') + texts.join('; '); })(),
      change: { occ: change(v => v.occ), revpar: change(v => v.revpar) },
    };
  }
  const MON = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  function stamp(iso) {                 // "4 Nov 03:20" (or "4 Nov" for a date only)
    if (!iso) return '';
    const [d, t] = String(iso).split('T');
    const [, m, dd] = d.split('-').map(Number);
    return `${dd} ${MON[m - 1]}` + (t ? ' ' + t.slice(0, 5) : '');
  }
  function part(card, cls, tag = 'span') {
    let el = card.querySelector('.' + cls);
    if (!el) {
      el = document.createElement(tag); el.className = cls;
      const pill = card.querySelector('.kpi-delta');           // coverage line first, then the change pill
      if (cls === 'kpi-sub' && pill) card.insertBefore(el, pill); else card.appendChild(el);
    }
    return el;
  }
  function delta(card, ch, kind) {
    const el = card.querySelector('.kpi-delta') || part(card, 'kpi-delta');
    if (!ch || ch.then == null || (kind !== 'pts' && !ch.then)) { el.textContent = ''; el.style.display = 'none'; el.className = 'kpi-delta'; return; }
    const d = kind === 'pts' ? ch.now - ch.then : (ch.now - ch.then) / ch.then * 100;
    el.style.display = '';
    el.textContent = `${d >= 0 ? '+' : '−'}${Math.abs(d).toFixed(1)}${kind === 'pts' ? ' pts' : '%'} vs 7 days earlier`;
    el.className = 'kpi-delta ' + (d >= 0 ? 'up pill--green' : 'down pill--red');
  }
  function noData(card, what) {
    const v = card.querySelector('.kpi-value');
    v.classList.remove('kpi-value--na');
    v.innerHTML = `<span class="pill--grey kpi-nodata-pill">${what}</span>`;
    card.querySelectorAll('.kpi-meta').forEach(e => { e.style.display = 'none'; });
  }
  function show(card, text, unit) {
    const v = card.querySelector('.kpi-value');
    v.classList.remove('kpi-value--na');
    v.textContent = text;
    let m = card.querySelector('.kpi-meta');
    if (!m && unit) { m = document.createElement('span'); m.className = 'kpi-meta'; v.after(m); }   // hotel cards: the range too
    if (m) { m.style.display = unit ? '' : 'none'; if (unit != null) m.textContent = unit; }
  }
  // ids: {occ, rate, revpar} card ids; list: the hotels behind them.
  // rate: BAR (published rate) since 3 Nov 2026, observed; occ and revpar:
  // Kodo estimates for the next 30 nights.
  async function cards(ids, list) {
    const els = Object.fromEntries(Object.entries(ids).map(([k, id]) => [k, document.getElementById(id)]).filter(([, e]) => e));
    const LABELS = { rate: 'BAR (published rate)', occ: 'Occupancy · Kodo estimate', revpar: 'Rooms RevPAR (est.)' };
    Object.entries(els).forEach(([k, c]) => { c.querySelector('.kpi-label').textContent = LABELS[k]; c.querySelector('.kpi-value').textContent = '…'; });
    const d = await load();
    if (!d) { Object.values(els).forEach(c => { noData(c, KodoBar.COLLECTING); part(c, 'kpi-sub').textContent = ''; }); return; }
    const a = agg(list), one = a.single, n = d.window.nights;
    const period = KodoPeriod.label({ kind: 'range', start: d.window.start, end: d.window.end });
    const occLine = `Next 30 nights · ${period}`;
    const cover = fig => one ? `estimated on ${one[fig + '_nights'] ?? 0} of ${n} nights`
      : `based on ${a[fig].n} of ${a.total} hotel${a.total === 1 ? '' : 's'}`;
    const tipOcc = KodoPeriod.tip({ source: `Kodo's occupancy model (${d.model === 'mixed' ? 'v2 where enough prices are collected, v1 elsewhere' : d.model === 'v2' ? 'v2' : 'v1'})${d.model_run ? ', run ' + stamp(d.model_run) : ''}`, note: a.calibrated ? CALIBRATED_LABEL + ', not measured' : 'Kodo estimate, not measured' });
    if (els.rate) KodoBar.card(els.rate, one ? { single: true, val: one.bar, nights: one.bar_nights || 0 } : a.bar, d);
    if (one && one.under_renovation) {             // hotel_flags.json: its BAR as usual, no occupancy or Rooms RevPAR
      [els.occ, els.revpar].filter(Boolean).forEach(c => { noData(c, RENOVATION_LABEL); part(c, 'kpi-sub').textContent = 'The hotel is partly open during works';
        c.title = 'This hotel is partly open while under renovation: it has no occupancy or Rooms RevPAR estimate, and its rooms are left out of the totals.'; });
      return;
    }
    if (one && one.seasonal_closure) {             // closed the whole window: no occupancy or Rooms RevPAR
      [els.occ, els.revpar].filter(Boolean).forEach(c => { noData(c, CLOSED_LABEL); part(c, 'kpi-sub').textContent = CLOSED_NOTE;
        c.title = `${CLOSED_NOTE}: no occupancy or Rooms RevPAR estimate for the coming 30 nights, and its rooms are left out of the totals.`; });
      return;
    }
    // Hover notes: the window each card covers and the hotels it includes
    const of = (k, what) => one ? '' : ` ${k} of ${a.total} hotel${a.total === 1 ? '' : 's'} ${what}.`;
    const hover = (c, t) => { if (c) c.title = t; };
    hover(els.rate, 'Window: past stay nights, from 3 November 2026 up to today (not the coming nights). For each night, the last published price seen before that night. '
      + (one ? `This hotel's BAR is the average of its ${one.bar_nights || 0} priced nights (it needs ${KodoBar.meta().min_nights}).`
             : `Each hotel's BAR is the average of its priced nights (it needs ${KodoBar.meta().min_nights}); this figure is the median of those hotel averages, not weighted by rooms.`
               + of(a.bar.n, `have enough published prices`)));
    hover(els.occ, `Window: the next 30 nights (${period}). ` + (a.calibrated ? CALIBRATED_LABEL : 'Kodo estimate') + ': modelled, not measured. ' + (a.basis ? a.basis + '. ' : '')
      + (one ? '' : 'Average weighted by rooms.' + of(a.occ.n, 'have an estimate'))
      + ' The change compares the same hotels 7 days earlier.');
    hover(els.revpar, `Window: the next 30 nights (${period}). For each hotel and night, the published price for that night times the estimated occupancy, `
      + 'averaged over the nights that have both' + (one ? '.' : '; hotels are then weighted by rooms.' + of(a.revpar.n, `have a BAR and ${KodoBar.meta().min_nights} priced coming nights (a group needs ${KodoBar.meta().min_hotels} such hotels)`))
      + ' So it is not the BAR card times the occupancy card: BAR covers past nights and is a median of hotels.'
      + ' The change compares the same hotels 7 days earlier.');
    // CONFIDENCE_UI (flags.py, off until approved): a plain label on the
    // modelled cards; greyed under medium, hidden when insufficient
    const conf = KODO_FLAG('CONFIDENCE_UI') && a.level;
    const CONF_TEXT = { high: 'Modelled · calibrated against real figures', medium: 'Modelled · medium confidence',
                        low: 'Limited data · low confidence', insufficient: 'Insufficient data' };
    const confLine = (c, level) => {
      const el = part(c, 'kpi-conf');
      el.textContent = level ? CONF_TEXT[level] : '';
      c.querySelector('.kpi-value').classList.toggle('kpi-value--limited', level === 'low');
    };
    if (els.occ) {
      const c = els.occ;
      KodoPeriod.setText(c, occLine, tipOcc);
      if (conf === 'insufficient') {
        noData(c, 'Insufficient data');
        part(c, 'kpi-sub').textContent = 'Not enough price history yet to model occupancy';
        confLine(c, null); delta(c, null);
      } else if (a.occ.val == null) { noData(c, KodoBar.COLLECTING); part(c, 'kpi-sub').textContent = ''; delta(c, null); }
      else {
        const range = a.low.val != null && a.high.val != null && a.low.n === a.occ.n
          ? `range ${Math.round(a.low.val)}–${Math.round(a.high.val)}%` : '';
        show(c, `${a.occ.val.toFixed(1)}%`, range ? range : (a.calibrated ? CALIBRATED_LABEL : 'Kodo estimate'));
        part(c, 'kpi-sub').textContent = (a.calibrated && range ? CALIBRATED_LABEL + ' · ' : '') + (a.basis ? a.basis + ' · ' : '') + cover('occ');
        delta(c, a.change.occ, 'pts');
        if (conf) confLine(c, conf);
      }
    }
    if (els.revpar) {
      const c = els.revpar;
      KodoPeriod.setText(c, `Next 30 nights · ${period}`, KodoPeriod.tip({ source: 'published BAR × Kodo occupancy estimate, night by night', note: 'Kodo estimate. ' + ROOMS_REVPAR_TIP }));
      if (conf === 'insufficient') { noData(c, 'Insufficient data'); part(c, 'kpi-sub').textContent = 'Not enough price history yet'; delta(c, null); }
      else if (!one && a.revpar.n > 0 && a.revpar.n < KodoBar.meta().min_hotels) { noData(c, KodoBar.LIMITED); part(c, 'kpi-sub').textContent = `${a.revpar.n} hotel${a.revpar.n === 1 ? '' : 's'} with ${KodoBar.meta().min_nights} priced nights: needs ${KodoBar.meta().min_hotels}`; delta(c, null); }
      else if (a.revpar.val == null) { noData(c, KodoBar.COLLECTING); part(c, 'kpi-sub').textContent = 'BAR × Kodo occupancy estimate'; delta(c, null); }
      else { const rr = a.rlow.val != null && a.rhigh.val != null && a.rlow.n === a.revpar.n ? ` · range ${fmt.mad(a.rlow.val)}–${fmt.mad(a.rhigh.val)}` : ''; show(c, fmt.mad(a.revpar.val), rr ? 'MAD' + rr : 'MAD · BAR × occupancy estimate'); part(c, 'kpi-sub').textContent = one ? `on ${one.occ_nights ?? 0} of ${n} nights` : cover('revpar'); delta(c, a.change.revpar, '%'); if (conf) confLine(c, conf); }
    }
  }
  return { load, agg, cards, stamp, part, noData, show, raw: () => data };
})();
// What a destination's occupancy estimate rests on (live_kpis.destination_confidence):
// {class: official | real | borrowed | national, label}, or null before the figures load
const destConf = city => (((KodoLive.raw() || {}).destinations) || {})[city] || null;
const isOfficial = city => (destConf(city) || {}).class === 'official';
// Display only: destination names with their accents. The keys (hotels.csv,
// ?dest=…, data-city) stay as they are, so ?dest=Saidia keeps working.
const DEST_DISPLAY = { 'Saidia': 'Saïdia', 'Laayoune': 'Laâyoune', 'Fes': 'Fès', 'Meknes': 'Meknès', 'Kenitra': 'Kénitra',
                       'Beni Mellal': 'Béni Mellal', 'Dades Valley': 'Dadès Valley' };
const dn = city => DEST_DISPLAY[city] || city;
const fold = t => String(t).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();   // search ignores accents
const escAttr = s => fmt.esc(s).replace(/"/g, '&quot;');

// The page's one disclaimer system: three badges (Official, Estimate,
// Limited data); the detail sits in the badge's tooltip, never in a sentence
const BADGE_TEXT = { official: 'Official', estimate: 'Estimate', limited: 'Limited data' };
function badgeHtml(kind, tip) {
  return `<span class="kodo-badge kodo-badge--${kind}" role="button" tabindex="0" data-tip="${escAttr(tip)}" aria-label="${BADGE_TEXT[kind]}: ${escAttr(tip)}">${BADGE_TEXT[kind]}</span>`;
}
const limitedBadge = tip => badgeHtml('limited', tip);
const DEST_BADGE_TIP = {
  official: 'Occupancy calibrated on official monthly figures for this destination.',
  borrowed: 'Estimate: levels borrowed from neighbouring destinations.',
  national: 'National estimate: the estimate does not use an official monthly series for this destination yet.',
};
function destBadge(city) {
  const c = destConf(city);
  if (!c) return '';
  if (c.class === 'official') return badgeHtml('official', DEST_BADGE_TIP.official);
  return badgeHtml('estimate', c.class === 'real' ? `Estimate: ${c.label.replace(/^Based/, 'based')}.` : DEST_BADGE_TIP[c.class] || DEST_BADGE_TIP.national);
}

// Tooltips for [data-tip]: on hover and keyboard focus, and on tap (touch has no hover)
const KodoTip = (() => {
  let pop = null, cur = null;
  function el() {
    if (!pop) { pop = document.createElement('div'); pop.className = 'kodo-tip-pop'; pop.id = 'kodo-tip-pop'; pop.setAttribute('role', 'tooltip'); pop.hidden = true; document.body.appendChild(pop); }
    return pop;
  }
  function show(t) {
    const p = el();
    p.textContent = t.dataset.tip; p.hidden = false; cur = t;
    t.setAttribute('aria-describedby', 'kodo-tip-pop');
    const r = t.getBoundingClientRect(), w = p.offsetWidth, h = p.offsetHeight;
    const x = Math.min(Math.max(8, r.left + r.width / 2 - w / 2), window.innerWidth - w - 8);
    const y = r.bottom + 6 + h > window.innerHeight - 8 ? r.top - h - 6 : r.bottom + 6;
    p.style.left = x + 'px'; p.style.top = Math.max(8, y) + 'px';
  }
  function hide() { if (pop) pop.hidden = true; if (cur) cur.removeAttribute('aria-describedby'); cur = null; }
  document.addEventListener('mouseover', e => {
    const t = e.target.closest && e.target.closest('[data-tip]');
    if (t) { if (t !== cur) show(t); } else if (cur && !cur.matches(':focus')) hide();
  });
  document.addEventListener('focusin', e => { const t = e.target.closest && e.target.closest('[data-tip]'); if (t) show(t); });
  document.addEventListener('focusout', () => hide());
  // a tap on a badge or an "i" shows its note and does not open the row it sits in
  document.addEventListener('click', e => {
    const t = e.target.closest && e.target.closest('.kodo-badge[data-tip], .kpi-info[data-tip], .k-info[data-tip], .k-badge[data-tip]');
    if (!t) { if (cur && !(e.target.closest && e.target.closest('[data-tip]'))) hide(); return; }
    e.stopPropagation(); e.preventDefault();
    if (cur === t && !pop.hidden) hide(); else show(t);
  }, true);
  document.addEventListener('keydown', e => { if (e.key === 'Escape') hide(); });
  window.addEventListener('scroll', hide, { passive: true, capture: true });
  return { show, hide };
})();

// Market Overview cards: a label, one big number and at most one short line;
// everything else the card says moves to its "i" tooltip
function compactDashCards(list) {
  const a = KodoLive.raw() ? KodoLive.agg(list) : null;
  compactKpiCards([
    { id: 'kpi-keys', label: 'Total keys', kind: 'keys' },
    { id: 'kpi-adr', label: 'BAR (median)', kind: 'adr' },
    { id: 'kpi-occ', label: 'Occupancy (est.)', kind: 'occ' },
    { id: 'kpi-revpar', label: 'Rooms RevPAR (est.)', kind: 'revpar' },
  ], a);
}
// A KPI card in the standard form: label, one number, one short line, and an
// "i" holding the window, the change and the card's own explanation.
// defs: [{ id, label, kind: keys | adr | occ | revpar, line?, badge? }]; a: KodoLive.agg of the cards' hotels (or null)
function compactKpiCards(defs, a) {
  const text = el => (el && el.style.display !== 'none' ? el.textContent.replace(/\s+/g, ' ').trim() : '');
  defs.forEach(({ id, label, kind, line: fixed, badge }) => {
    const c = document.getElementById(id);
    if (!c) return;
    c.querySelector('.kpi-label').textContent = label;
    const v = c.querySelector('.kpi-value'), meta = c.querySelector('.kpi-meta'), sub = c.querySelector('.kpi-sub');
    const delta = c.querySelector('.kpi-delta'), period = c.querySelector('.kpi-period'), conf = c.querySelector('.kpi-conf');
    const figure = !v.querySelector('.kpi-nodata-pill');
    // the window, the change, why there is no figure (if none), then the card's own explanation
    const notes = [text(period), text(delta), figure ? '' : text(sub), text(conf), c.title].filter(Boolean);
    c.removeAttribute('title');
    const range = (text(meta).match(/range [^·]+/i) || [''])[0].trim();
    let line = '';
    if (fixed != null) line = fixed;
    else if (kind === 'keys') line = text(meta);
    else if (kind === 'adr') line = figure && a && !a.single ? `median of ${a.bar.n} hotels` : figure ? text(sub) : '';
    else if (figure) line = range ? range.replace(/^RANGE/i, 'range') : text(delta);
    if (figure && (kind === 'adr' || kind === 'revpar') && !v.querySelector('.kpi-unit')) v.insertAdjacentHTML('beforeend', '<span class="kpi-unit">MAD</span>');
    let ln = c.querySelector('.kpi-line');
    if (!ln) { ln = document.createElement('span'); ln.className = 'kpi-line'; v.after(ln); }
    ln.innerHTML = (badge ? badge + ' ' : '') + fmt.esc(line);
    let i = c.querySelector('.kpi-info');
    if (!i) { i = document.createElement('button'); i.type = 'button'; i.className = 'kpi-info'; i.textContent = 'i'; c.appendChild(i); }
    i.dataset.tip = notes.join(' · ');
    i.setAttribute('aria-label', `About ${label}: ${notes.join('. ')}`);
  });
}

// ─── Aggregation ──────────────────────────────────────────────────

// A group of hotels: BAR (observed, median of its hotels' BAR, see
// KodoBar) and the Kodo estimates (occupancy and Rooms RevPAR, next 30 nights,
// room-weighted over the hotels that have them; null when none has).
function perfAggs(hs) {
  const has = (h, k) => h[k] != null && !Number.isNaN(Number(h[k]));
  const avg = k => {
    const rows = hs.filter(h => has(h, k) && (h.keys || 0) > 0);
    const den = rows.reduce((s, h) => s + h.keys, 0);
    return den ? rows.reduce((s, h) => s + h[k] * h.keys, 0) / den : null;
  };
  // Rooms RevPAR: the BAR minimum, 3 hotels with a Rooms RevPAR (each needs 7 priced nights) or "limited data"
  const rn = hs.filter(h => has(h, 'revpar_mad') && (h.keys || 0) > 0).length;
  const revpar_limited = rn > 0 && rn < KodoBar.meta().min_hotels;
  return { bar: KodoBar.group(hs), occupancy: avg('occupancy'), revpar_mad: revpar_limited ? null : avg('revpar_mad'),
           revpar_hotels: rn, revpar_limited };
}

function cityAggs(hotelList) {
  const map = new Map();
  hotelList.forEach(h => {
    if (!map.has(h.city)) map.set(h.city, []);
    map.get(h.city).push(h);
  });
  return [...map.entries()].map(([city, hs]) => ({
    city, hotel_count: hs.length, total_keys: hs.reduce((s, h) => s + (h.keys || 0), 0), ...perfAggs(hs),
  }));
}

function brandAggs(hotelList) {
  const map = new Map();
  hotelList.forEach(h => {
    if (!map.has(h.brand_group)) map.set(h.brand_group, []);
    map.get(h.brand_group).push(h);
  });
  return [...map.entries()].map(([bg, hs]) => ({
    brand_group: bg, hotel_count: hs.length, total_keys: hs.reduce((s, h) => s + (h.keys || 0), 0), ...perfAggs(hs),
  })).sort((a, b) => b.total_keys - a.total_keys);
}

function filteredByCity() {
  if (state.city === 'all') return hotels;
  return hotels.filter(h => h.city === state.city);
}

// Destinations ranked by BAR: figures first (high to low), then "limited
// data" (high to low), then the ones with no BAR yet (A–Z)
function rankedCities() {
  const rank = c => (c.bar.val == null ? 2 : c.bar.limited ? 1 : 0);
  return cityAggs(hotels || []).sort((a, b) => rank(a) - rank(b) || (b.bar.val || 0) - (a.bar.val || 0) || a.city.localeCompare(b.city));
}

// ─── KPIs ─────────────────────────────────────────────────────────

function renderKPIs() {
  const list = filteredByCity();
  const keys = list.reduce((s, h) => s + (h.keys || 0), 0);
  const hotelLabel = list.length + ' hotel' + (list.length !== 1 ? 's' : '');
  const kc = document.getElementById('kpi-keys');
  kc.querySelector('.kpi-value').textContent = fmt.num(keys);
  document.getElementById('kpi-keys-meta').textContent = hotelLabel;
  kc.classList.remove('loading');
  KodoPeriod.set('kpi-keys', KodoPeriod.today(), COUNT_TIP);
  const reno = list.filter(h => h.under_renovation).length;
  const shut = list.filter(h => h.seasonal_closure).length;
  kc.title = `Today's count from Kodo's hotel database: ${list.length} open hotel${list.length === 1 ? '' : 's'} and their ${fmt.num(keys)} rooms.`
    + (reno ? ` Excludes ${reno === 1 ? 'a hotel' : reno + ' hotels'} under renovation.` : '')
    + (shut ? ` Excludes the rooms of ${shut === 1 ? 'a hotel' : shut + ' hotels'} closed for the season (${CLOSED_NOTE.toLowerCase()}).` : '');
  // BAR: observed since 3 Nov 2026. Occupancy, Rooms RevPAR: Kodo estimates, next 30 nights (KodoLive)
  ['kpi-occ', 'kpi-adr', 'kpi-revpar'].forEach(id => document.getElementById(id).classList.remove('loading'));
  KodoLive.cards({ occ: 'kpi-occ', rate: 'kpi-adr', revpar: 'kpi-revpar' }, list).then(() => compactDashCards(list));
  const sub = document.getElementById('dashboard-sub');
  sub.textContent = state.city === 'all' ? 'Morocco hotel market' : `${dn(state.city)} · ${hotelLabel}`;
}

// ─── Charts ───────────────────────────────────────────────────────

// Hex colour + alpha → rgba() (Chart.js draws on canvas, so no CSS variables)
function withAlpha(hex, a) {
  const h = hex.replace('#', '');
  const n = parseInt(h.length === 3 ? h.split('').map(c => c + c).join('') : h, 16);
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
}

// Chart colours, read from the palette for the current theme (palette.js).
// Series order: blue, green, orange, violet, sky, grey (dot colours).
function getChartColors() {
  const p = KodoPalette.get();
  return {
    barColor:   p.series[0],
    barColor2:  p.series[1],
    barColor3:  p.series[2],
    barColor4:  p.series[3],
    series:     p.series,
    compColor:  p.series[5],                 // comp-set / benchmark reference: grey
    hoverColor: p.families.blue.text,       // highlighted bar: black (white in dark): no blue on the platform
    forecastColor: p.series[1],              // forecast years: mid grey (the lightest greys vanish at 45%)
    fillColor:  withAlpha(p.series[0], 0.12),
    gridColor:  p.grid,
    tick:       p.text2,                     // axis text (--text-3 is below AA at 11px)
    label:      p.text2,
    catLabel:   p.text,
    tooltipBg:  p.tooltipBg,
    tooltipBdr: p.tooltipBorder,
    tooltipTtl: p.text,
    tooltipBdy: p.text2,
    pointBorder: p.bg,
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
        maxBarThickness: 28,
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 350 },
      layout: { padding: { right: 72, left: 8 } },
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
          ticks: { color: cc.tick, font: { size: 11, weight: '400', family: "'Sweet Sans Pro', sans-serif" }, padding: 4 }
        },
        y: {
          ticks: { color: cc.catLabel, font: { size: 12, weight: '500' }, padding: 10 }
        }
      }
    }
  };
}

// Lighter type for the dense city-name charts (axis ticks and bar labels)
function lightenCityChartLabels(cfg) {
  const color = KodoPalette.get().text2;
  const font = { family: 'Sweet Sans Pro', size: 11, weight: '200' };
  cfg.options.scales.y.ticks.font = font;
  cfg.options.scales.y.ticks.color = color;
  cfg.options.plugins.datalabels.font = font;
  cfg.options.plugins.datalabels.color = color;
  return cfg;
}

// A chart card's canvas or its "Collecting data" state
function chartOrCollecting(canvasId, empty, detail) {
  const wrap = document.getElementById(canvasId).closest('.chart-wrap');
  let box = wrap.parentElement.querySelector('.collecting-state');
  if (empty) {
    wrap.style.display = 'none';
    if (!box) { wrap.insertAdjacentHTML('afterend', KodoBar.collecting(detail)); }
    return false;
  }
  if (box) box.remove();
  wrap.style.display = '';
  return true;
}

// ─── Destination list (sidebar; chips under 768 px) ───────────────

// The sidebar number: BAR (MAD, observed) or occupancy (%, Kodo estimate,
// next 30 nights), the same figures as the two charts
const DEST_METRIC_LABEL = { bar: 'Destination · BAR (MAD)', occ: 'Destination · Occ. % (est.)' };
function destMetricVal(c) {
  if (state.destMetric === 'occ') {
    if (c.occupancy == null) return { html: '<span class="dest-val dest-val--na">—</span>', v: null, what: 'no occupancy estimate', est: false };
    const est = !isOfficial(c.city);
    const pct = (c.occupancy * 100).toFixed(1);
    return { html: `<span class="dest-val">${pct}%</span>`, v: c.occupancy, est, what: `occupancy ${pct}%, ${est ? 'estimate' : 'official'}` };
  }
  return { html: c.bar.val == null ? '<span class="dest-val dest-val--na">—</span>'
    : c.bar.limited ? `<span class="dest-val dest-val--limited">${KodoBar.LIMITED}</span>`
    : `<span class="dest-val">${fmt.mad(c.bar.val)}</span>`, v: c.bar.limited ? null : c.bar.val, est: false,
    what: c.bar.val == null ? 'no BAR yet' : c.bar.limited ? 'BAR limited data' : `BAR ${fmt.mad(c.bar.val)} MAD` };
}

function destRowHtml(c, max) {
  const sel = c.city === state.city;
  const m = destMetricVal(c);
  const w = m.v != null && max ? Math.max(2, Math.round(m.v / max * 100)) : 0;
  return `<li class="dest-row${sel ? ' is-selected' : ''}" role="option" aria-selected="${sel}" tabindex="${sel ? 0 : -1}"
      data-city="${escAttr(c.city)}" aria-label="${escAttr(dn(c.city))}, ${c.hotel_count} hotels, ${m.what}">
    <span class="dest-line"><span class="dest-name">${fmt.esc(dn(c.city))}</span><span class="dest-count">${c.hotel_count}</span>${m.html}</span>
    <span class="dest-meter${m.est ? ' dest-meter--est' : ''}" aria-hidden="true"><span style="width:${w}%"></span></span>
  </li>`;
}

// Destinations in the order of the sidebar's number (high to low, then none, A–Z)
function sidebarCities() {
  if (state.destMetric !== 'occ') return rankedCities();
  return cityAggs(hotels || []).sort((a, b) => (a.occupancy == null) - (b.occupancy == null)
    || (b.occupancy || 0) - (a.occupancy || 0) || a.city.localeCompare(b.city));
}

function setDestMetric(m) {
  state.destMetric = m === 'occ' ? 'occ' : 'bar';
  dashPrefs.set('metric', state.destMetric);
  document.getElementById('dest-label').textContent = DEST_METRIC_LABEL[state.destMetric];
  document.querySelectorAll('.dest-metric-btn').forEach(b => {
    const on = b.dataset.metric === state.destMetric;
    b.classList.toggle('is-on', on); b.setAttribute('aria-pressed', on);
  });
  buildCityFilter();
}

function buildCityFilter() {
  const list = document.getElementById('city-filter');
  const rows = sidebarCities();
  const max = Math.max(0, ...rows.map(r => destMetricVal(r).v).filter(v => v != null));
  const all = state.city === 'all';
  document.getElementById('dest-label').textContent = DEST_METRIC_LABEL[state.destMetric];   // the header always matches the toggle
  list.innerHTML = `<li class="dest-row dest-row--all${all ? ' is-selected' : ''}" role="option" aria-selected="${all}" tabindex="${all ? 0 : -1}"
      data-city="all" aria-label="All Morocco, ${(hotels || []).length} hotels">
      <span class="dest-line"><span class="dest-name">All Morocco</span><span class="dest-count">${(hotels || []).length} hotels</span></span></li>`
    + rows.map(c => destRowHtml(c, max)).join('');
  filterDestRows();
  buildMobileCityPills(rows);
}

function filterDestRows() {
  const q = (document.getElementById('dest-search')?.value || '').trim().toLowerCase();
  document.querySelectorAll('#city-filter .dest-row:not(.dest-row--all)').forEach(li => {
    li.hidden = !!q && !fold(dn(li.dataset.city)).includes(fold(q));
  });
  document.querySelectorAll('#mobile-city-pills [data-mcity]:not([data-mcity="all"])').forEach(b => {
    b.hidden = !!q && !fold(dn(b.dataset.mcity)).includes(fold(q));
  });
  const empty = document.getElementById('dest-empty');
  if (empty) empty.hidden = !q || [...document.querySelectorAll('#city-filter .dest-row:not(.dest-row--all)')].some(li => !li.hidden);
}

// Select a destination everywhere (list, chips, charts, the rest of the
// dashboard): only classes change, so the list keeps its scroll position
function selectCity(city) {
  state.city = city || 'all';
  writeDashUrl();
  document.querySelectorAll('#city-filter .dest-row').forEach(li => {
    const on = li.dataset.city === state.city;
    li.classList.toggle('is-selected', on);
    li.setAttribute('aria-selected', on);
    li.tabIndex = on ? 0 : -1;
  });
  document.querySelectorAll('#mobile-city-pills [data-mcity]').forEach(b => {
    const on = b.dataset.mcity === state.city;
    b.classList.toggle('active', on);
    b.setAttribute('aria-pressed', on);
  });
  // bring the row into view inside its own box only (the page does not move)
  const box = document.getElementById('dest-box');
  const row = document.querySelector(`#city-filter .dest-row[data-city="${CSS.escape(state.city)}"]`);
  if (box && row && !row.hidden) {
    const top = row.offsetTop - box.offsetTop, bottom = top + row.offsetHeight;
    if (top < box.scrollTop) box.scrollTop = top;
    else if (bottom > box.scrollTop + box.clientHeight) box.scrollTop = bottom - box.clientHeight;
  }
  render();
}

// ─── Brand table ──────────────────────────────────────────────────

// Rows whose shown occupancy is the same as another row's: those hotels have
// no hotel-specific signal yet and carry the destination's estimate for their
// type of hotel, so identical figures are expected (not a bug)
const SHARED_OCC_TIP = 'Destination-level estimate. Same figure as other rows: these hotels have no hotel-specific signal yet, so they carry the destination-level estimate for their type of hotel.';
function sharedOcc(rows) {
  const n = {};
  rows.forEach(r => { const k = fmt.pct(r.occupancy); if (r.occupancy != null) n[k] = (n[k] || 0) + 1; });
  return r => r.occupancy != null && n[fmt.pct(r.occupancy)] > 1;
}

// Rooms RevPAR in a table: the figure, with how many published prices of the
// coming 30 nights it rests on (live_kpis.py rate_nights)
function revparCell(value, hs, limited) {
  const m = KodoBar.meta();
  const L = (KodoLive.raw() || {}).hotels || {};
  const priced = hs.map(h => L[String(h.id)]).filter(v => v && v.revpar != null);
  if (limited) return limitedBadge(`Rooms RevPAR (est.): ${priced.length} hotel${priced.length === 1 ? '' : 's'} with ${m.min_nights} priced nights; a group needs ${m.min_hotels}.`);
  if (value == null) return `<span class="bar-na" title="Rooms RevPAR needs a BAR (${m.min_nights} priced past nights) and ${m.min_nights} coming nights with a published price (occupancy does not)">—</span>`;
  const nights = priced.reduce((s, v) => s + (v.revpar_nights || 0), 0);
  const tip = priced.length ? `Kodo estimate: published price × modelled occupancy over the coming 30 nights · ${priced.length} hotel${priced.length === 1 ? '' : 's'}, ${nights} priced night${nights === 1 ? '' : 's'}` : EST_TIP;
  return `<span title="${tip}">${fmt.mad(value)}</span>`;
}

function renderBrandTable() {
  const list = filteredByCity();
  const rows = brandAggs(list);
  const tbody = document.querySelector('#brand-table tbody');
  const shared = sharedOcc(rows);

  tbody.innerHTML = rows.map((r, i) => `
    <tr>
      <td class="rank-cell col-hide-mobile">${i + 1}</td>
      <td><button class="brand-link" data-brand="${fmt.esc(r.brand_group)}" onclick="showBrandDetail(this.dataset.brand)">${getBrandLogoImg(r.brand_group, 20)} ${fmt.esc(r.brand_group)}</button></td>
      <td class="col-hide-mobile">${r.hotel_count}</td>
      <td>${fmt.num(r.total_keys)}</td>
      <td>${brandBarCell(r.bar)}</td>
      <td>${shared(r) ? `<span data-tip="${escAttr(SHARED_OCC_TIP)}">${fmt.pct(r.occupancy)}</span>` : fmt.pct(r.occupancy)}</td>
      <td>${revparCell(r.revpar_mad, list.filter(h => h.brand_group === r.brand_group), r.revpar_limited)}</td>
    </tr>
  `).join('');
  // the rules sit in the column headers' tooltips, not under the table
  const m = KodoBar.meta();
  document.getElementById('brand-th-bar').dataset.tip = `BAR (published rate): the median of the group's hotels that have ${m.min_nights} or more priced past nights since 3 Nov 2026. Limited data under ${m.min_hotels} such hotels, "—" with none.`;
  document.getElementById('brand-th-revpar').dataset.tip = `Rooms RevPAR (est.): published price × estimated occupancy over the next 30 nights. A hotel counts once it has a BAR and ${m.min_nights} priced coming nights; limited data under ${m.min_hotels} such hotels, "—" with none. Occupancy needs no price, so it can show without Rooms RevPAR.`;
}
// A group's BAR in the destination's Brands table: the figure, the Limited data badge, or "—"
function brandBarCell(g) {
  if (!g || g.val == null) return '<span class="cell-na">—</span>';
  if (g.limited) return limitedBadge(`${g.n} hotel${g.n === 1 ? '' : 's'} with ${KodoBar.meta().min_nights} priced nights; a group needs ${KodoBar.meta().min_hotels}.`);
  return `<span data-tip="${escAttr(`Median of ${g.n} hotels' BAR · ${g.nights} priced nights`)}">${fmt.mad(g.val)}</span>`;
}

// ─── Scope: All Morocco (compare destinations) or one destination (tabs) ───

const DASH_TABS = ['overview', 'hotels', 'brands'];   // an old ?tab=seasonality opens Overview (the chart is there now)
const dashPrefs = {          // remembered per browser; the page works without it
  get: k => { try { return localStorage.getItem('kodo.dash.' + k); } catch { return null; } },
  set: (k, v) => { try { localStorage.setItem('kodo.dash.' + k, v); } catch { /* private mode */ } },
};

// /dashboard?dest=Saidia&tab=hotels: a link to a destination and tab can be shared
function readDashUrl() {
  const q = new URLSearchParams(location.search);
  const cities = new Set((hotels || []).map(h => h.city));
  const dest = q.get('dest');
  if (dest && cities.has(dest)) state.city = dest;
  const tab = q.get('tab') || dashPrefs.get('tab');
  state.tab = DASH_TABS.includes(tab) ? tab : 'overview';
  state.destMetric = dashPrefs.get('metric') === 'occ' ? 'occ' : 'bar';
}
function writeDashUrl() {
  const q = new URLSearchParams(location.search);
  q.delete('dest'); q.delete('tab');
  if (state.city !== 'all') { q.set('dest', state.city); q.set('tab', state.tab); }
  const s = q.toString();
  try { history.replaceState(history.state, '', location.pathname + (s ? '?' + s : '') + location.hash); } catch { /* file:// */ }
}

function selectTab(tab) {
  state.tab = DASH_TABS.includes(tab) ? tab : 'overview';
  dashPrefs.set('tab', state.tab);
  writeDashUrl();
  applyDashScope();
  renderSeason();
}

// One destination, Seasonality: the past 12 months' official monthly figures
// (solid; months without one are gaps, never zero) and the next 12 months'
// Kodo estimate with its range (dashed line over a light band), both read
// as stored (/api/destination-seasonality: no estimate is made for the page)
let seasonChart = null;
const seasonCache = {};
const MON3S = m => ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][+m.slice(5) - 1] + ' ' + m.slice(2, 4);
async function renderSeason() {
  if (state.city === 'all' || state.tab !== 'overview') return;
  const city = state.city;
  const note = document.getElementById('season-note');
  let d = seasonCache[city];
  if (!d) {
    try { const r = await fetch('/api/destination-seasonality?city=' + encodeURIComponent(city)); d = r.ok ? await r.json() : null; } catch { d = null; }
    if (!d) { note.textContent = 'Not available right now'; note.hidden = false; return; }
    seasonCache[city] = d;
  }
  if (state.city !== city || state.tab !== 'overview') return;
  const p = KodoPalette.get(), blue = p.families.blue.dot, cc = getChartColors();
  const past = d.past || [], next = d.next || [];
  // one continuous timeline: months between the last official one and the
  // first estimated one (the latest month not yet published, this month) stay empty
  const months = [];
  const step = m => { const y = +m.slice(0, 4), mo = +m.slice(5); return mo === 12 ? `${y + 1}-01` : `${y}-${String(mo + 1).padStart(2, '0')}`; };
  const first = (past[0] || next[0] || {}).month, last = (next[next.length - 1] || past[past.length - 1] || {}).month;
  for (let m = first; m && m <= last && months.length < 36; m = step(m)) months.push(m);
  const P = Object.fromEntries(past.map(x => [x.month, x])), N = Object.fromEntries(next.map(x => [x.month, x]));
  const labels = months.map(MON3S);
  const official = months.map(m => (P[m] && P[m].status === 'official' ? P[m].occ : null));
  // estimates: the next 12 months, and a published figure whose month the release did not state
  const est = months.map(m => (N[m] ? N[m].occ : P[m] && P[m].status === 'estimated' ? P[m].occ : null));
  const tipFor = m => {
    if (P[m] && P[m].status === 'estimated') return '  Estimate: published figure, month not stated';
    const n = N[m];
    return n && n.low != null && n.high != null ? `  Range ${Math.round(n.low)}–${Math.round(n.high)}%` : '';
  };
  const cfg = {
    type: 'bar',
    data: { labels, datasets: [
      { label: 'Official', data: official, backgroundColor: blue, borderRadius: 3, maxBarThickness: 26, grouped: false },
      { label: 'Estimate', data: est, backgroundColor: withAlpha(blue, 0.3), borderRadius: 3, maxBarThickness: 26, grouped: false },
    ] },
    options: {
      responsive: true, maintainAspectRatio: false, animation: { duration: 250 },
      plugins: {
        legend: { display: false }, datalabels: { display: false },
        tooltip: { backgroundColor: cc.tooltipBg, borderColor: cc.tooltipBdr, borderWidth: 1, titleColor: cc.tooltipTtl, bodyColor: cc.tooltipBdy,
          filter: it => it.raw != null,
          callbacks: {
            label: it => `  ${it.dataset.label}: ${(+it.raw).toFixed(it.dataset.label === 'Official' ? 0 : 1)}%`,
            afterLabel: it => (it.dataset.label === 'Estimate' ? tipFor(months[it.dataIndex]) : ''),
          } },
      },
      scales: {
        x: { ticks: { color: cc.tick, font: { size: 10 }, maxRotation: 0, autoSkip: true }, grid: { display: false } },
        y: { min: 0, max: 100, ticks: { color: cc.tick, font: { size: 11 }, callback: v => v + '%' }, grid: { color: cc.gridColor } },
      },
    },
  };
  if (seasonChart) seasonChart.destroy();
  seasonChart = new Chart(document.getElementById('chart-season'), cfg);
  // one short line, only when the destination has no official series
  note.textContent = 'Estimate only';
  note.hidden = past.some(p => p.status === 'official');
}

function applyDashScope() {
  const mode = state.city === 'all' ? 'all' : state.tab;
  document.getElementById('dash-scope').hidden = state.city === 'all';
  document.querySelectorAll('#screen-dashboard [data-dash]').forEach(el => { el.hidden = !el.dataset.dash.split(' ').includes(mode); });
  document.querySelectorAll('#dash-scope [data-tab]').forEach(b => {
    const on = b.dataset.tab === state.tab;
    b.classList.toggle('active', on); b.setAttribute('aria-selected', on);
  });
}

// All Morocco: one row per destination (Destination | Hotels | Keys | BAR |
// Occupancy (est.) | badge), sortable by any header, default keys high to
// low. Inline bars: solid = Official, light = Estimate, none for limited
// data; blue only for the selected destination.
const destSort = { key: 'keys', dir: -1 };
const DEST_SORT_VAL = {
  city: c => fold(dn(c.city)), hotels: c => c.hotel_count, keys: c => c.total_keys,
  bar: c => (c.bar.val == null || c.bar.limited ? null : c.bar.val), occ: c => c.occupancy,
  badge: c => ({ official: 0, real: 1, borrowed: 1, national: 1 }[(destConf(c.city) || {}).class] ?? 2),
};
function sortedCities() {
  const f = DEST_SORT_VAL[destSort.key] || DEST_SORT_VAL.keys;
  return cityAggs(hotels || []).sort((a, b) => {
    const x = f(a), y = f(b);
    if (x == null || y == null) return (x == null) - (y == null) || a.city.localeCompare(b.city);   // no figure: last
    const d = typeof x === 'string' ? x.localeCompare(y) : x - y;
    return d * destSort.dir || a.city.localeCompare(b.city);
  });
}
function inlineBar(v, max, est, sel) {
  if (v == null || !max) return '';
  return `<span class="ibar${est ? ' ibar--est' : ''}${sel ? ' ibar--sel' : ''}" aria-hidden="true"><span style="width:${Math.max(2, Math.round(v / max * 100))}%"></span></span>`;
}
function renderDestTable() {
  const table = document.getElementById('dest-table');
  if (!table) return;
  const rows = sortedCities();
  const all = cityAggs(hotels || []);
  const maxBar = Math.max(0, ...all.map(c => DEST_SORT_VAL.bar(c)).filter(v => v != null));
  const maxOcc = Math.max(0, ...all.map(c => c.occupancy).filter(v => v != null));
  table.querySelector('tbody').innerHTML = rows.map(c => {
    const sel = c.city === state.city, est = !isOfficial(c.city);
    const bar = c.bar.val == null ? '<span class="cell-na">—</span>'
      : c.bar.limited ? limitedBadge(`BAR: ${c.bar.n} hotel${c.bar.n === 1 ? '' : 's'} with ${KodoBar.meta().min_nights} priced nights; a destination needs ${KodoBar.meta().min_hotels}.`)
      : `<span class="cell-num">${fmt.mad(c.bar.val)}</span>${inlineBar(c.bar.val, maxBar, false, sel)}`;
    const occ = c.occupancy == null ? '<span class="cell-na">—</span>'
      : `<span class="cell-num">${fmt.pct(c.occupancy)}</span>${inlineBar(c.occupancy, maxOcc, est, sel)}`;
    return `<tr data-city="${escAttr(c.city)}" tabindex="0"${sel ? ' class="is-selected"' : ''}>
      <td class="cell-dest">${fmt.esc(dn(c.city))}<span class="badge-m">${destBadge(c.city)}</span></td>
      <td class="col-hide-mobile">${c.hotel_count}</td>
      <td>${fmt.num(c.total_keys)}</td>
      <td class="cell-metric">${bar}</td>
      <td class="cell-metric">${occ}</td>
      <td class="col-hide-mobile">${destBadge(c.city)}</td>
    </tr>`;
  }).join('');
  table.querySelectorAll('th[data-sort]').forEach(th => {
    th.setAttribute('aria-sort', th.dataset.sort === destSort.key ? (destSort.dir > 0 ? 'ascending' : 'descending') : 'none');
  });
}
function sortDestTable(key) {
  if (destSort.key === key) destSort.dir = -destSort.dir;
  else { destSort.key = key; destSort.dir = key === 'city' || key === 'badge' ? 1 : -1; }
  renderDestTable();
}

// One destination, Hotels tab: its hotels with their status (hotel_flags.json)
function renderDestHotels() {
  const tbody = document.querySelector('#dest-hotels-table tbody');
  if (!tbody || state.city === 'all') return;
  const list = filteredByCity().slice().sort((a, b) => (b.keys_listed ?? b.keys ?? 0) - (a.keys_listed ?? a.keys ?? 0) || a.name.localeCompare(b.name));
  const status = h => h.under_renovation ? 'Partly open, under renovation' : h.seasonal_closure ? CLOSED_NOTE : '';
  tbody.innerHTML = list.map(h => `<tr class="hotel-row-link" onclick="showHotelDetail(${h.id})">
      <td class="hotel-name-cell"><button class="hotel-name-btn">${fmt.esc(h.name)}</button></td>
      <td class="col-hide-mobile">${getSegmentBadgeHtml(h.category)}</td>
      <td class="col-hide-mobile">${getBrandLogoImg(h.brand_group, 16)} ${fmt.esc(h.brand_group)}</td>
      <td title="${h.under_renovation || h.seasonal_closure ? 'Listed rooms; left out of the totals while ' + (h.under_renovation ? 'under renovation' : 'closed for the season') : ''}">${fmt.num(h.under_renovation || h.seasonal_closure ? h.keys_listed : h.keys)}</td>
      <td>${KodoBar.hotelCell(h)}</td>
      <td title="${EST_TIP}">${hotelOcc(h)}</td>
      <td class="col-hide-mobile">${revparCell(h.revpar_mad, [h])}</td>
      <td><span class="hotel-status">${status(h) || '—'}</span></td>
    </tr>`).join('');
}

// The page head: the subtitle, the destination's badge, and the one line
// that says what is observed and what is estimated (the real dates)
function renderDashHead() {
  const d = KodoLive.raw();
  const est = d && d.window ? ` (${KodoPeriod.label({ kind: 'range', start: d.window.start, end: d.window.end })})` : '';
  document.getElementById('dash-explain').textContent =
    `Prices: observed since 3 Nov 2026. Occupancy and Rooms RevPAR: Kodo estimate for the next 30 nights${est}.`;
  document.getElementById('dash-badge').innerHTML = state.city === 'all' ? '' : destBadge(state.city);
}

// ─── Brands screen ────────────────────────────────────────────────

async function initBrands() {
  if (!brandsInited) {
    try {
      brandsData   = await fetch('/api/brands').then(r => r.json());
      brandsInited = true;
    } catch (e) {
      document.getElementById('brands-comp-tbody').innerHTML = '<tr><td colspan="8" class="k-empty">Failed to load brand data.</td></tr>';
      return;
    }
  }
  renderBrandsKPIs();
  brandsSetView(brandsSavedView(), false);
  renderBrands();
}

// Brands: title + one line, four cards, one row of controls, one main view
// (sortable table by default, or compact cards); row or card opens the brand page
const BRANDS_VIEWS = ['table', 'cards'];
function brandsSavedView() {
  try { const v = localStorage.getItem('kodo.brands.view'); return BRANDS_VIEWS.includes(v) ? v : 'table'; } catch { return 'table'; }
}
function brandsSetView(view, save = true) {
  document.querySelectorAll('#brands-view [data-view]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.view === view)));
  document.querySelectorAll('#screen-brands [data-bview]').forEach(v => { v.hidden = v.dataset.bview !== view; });
  if (save) try { localStorage.setItem('kodo.brands.view', view); } catch { /* private window */ }
}

function filteredBrands() {
  let data = [...brandsData];
  if (brandsFilter.segment !== 'all') data = data.filter(b => b.segments.includes(brandsFilter.segment));
  const q = fold(brandsFilter.search.trim());
  if (q) data = data.filter(b => fold(b.brand_group).includes(q));
  const k = brandsFilter.sort, dir = brandsFilter.dir;
  // a limited BAR or Rooms RevPAR sorts with the groups that have none
  const val = b => k === 'bar_mad' && b.bar_limited ? null : k === 'avg_revpar' && b.revpar_limited ? null : b[k];
  data.sort((a, b) => {
    if (BRANDS_STR_COLS.has(k)) return dir * String(a[k]).localeCompare(String(b[k]));
    const x = val(a), y = val(b);
    if (x == null || y == null) return (x == null) - (y == null) || a.brand_group.localeCompare(b.brand_group);
    return dir * (x - y) || a.brand_group.localeCompare(b.brand_group);
  });
  return data;
}

function renderBrands() {
  if (!brandsData) return;
  const data = filteredBrands();
  document.getElementById('brands-count').textContent = `${data.length} of ${brandsData.length} groups`;
  document.querySelectorAll('#brands-comp-table th[data-bccol]').forEach(th => {
    if (th.dataset.bccol === brandsFilter.sort) th.setAttribute('aria-sort', brandsFilter.dir === 1 ? 'ascending' : 'descending');
    else th.removeAttribute('aria-sort');
  });
  const sel = document.getElementById('brands-sort');
  if (sel.querySelector(`option[value="${brandsFilter.sort}"]`)) sel.value = brandsFilter.sort;
  renderBrandsCompTable(data);
  renderBrandsCards(data);
}

function renderBrandsKPIs() {
  const branded = brandsData.filter(b => !/^Independent/.test(b.brand_group));
  const brandedKeys = branded.reduce((s, b) => s + b.total_keys, 0);
  const largest = [...brandsData].sort((a, b) => b.total_keys - a.total_keys)[0];
  const today = KodoPeriod.label(KodoPeriod.today());
  const card = (id, value, line, tip) => {
    const c = document.getElementById(id);
    c.querySelector('.kpi-value').textContent = value;
    c.title = tip || '';
  };
  card('brnkpi-groups', brandsData.length, '', COUNT_TIP);
  card('brnkpi-keys', brandedKeys.toLocaleString('en'), '', `${COUNT_TIP}. Branded: every group except independent hotels (${(brandsData.reduce((s, b) => s + b.total_keys, 0) - brandedKeys).toLocaleString('en')} keys).`);
  card('brnkpi-largest', largest ? largest.brand_group : '—', '', largest ? `${COUNT_TIP}. By keys: ${largest.total_keys.toLocaleString('en')} keys, ${largest.hotels} hotels.` : '');
  // Highest BAR among groups whose BAR rests on 3 hotels or more (observed since 3 Nov 2026)
  const best = [...brandsData].filter(b => b.bar_mad != null && !b.bar_limited).sort((x, y) => y.bar_mad - x.bar_mad)[0];
  const ch = document.getElementById('brnkpi-champion');
  if (!best) ch.querySelector('.kpi-value').innerHTML = `<span class="pill--grey kpi-nodata-pill">${KodoBar.COLLECTING}</span>`;
  else ch.querySelector('.kpi-value').textContent = best.brand_group;
  ch.title = `BAR (published rate) · ${KodoBar.caption()} · median of the group's hotels; only groups with ${KodoBar.meta().min_hotels} hotels or more with ${KodoBar.meta().min_nights} priced nights.`;
  compactKpiCards([
    { id: 'brnkpi-groups', label: 'Brand groups', kind: 'keys', line: `incl. independent hotels · ${today}` },
    { id: 'brnkpi-keys', label: 'Total branded keys', kind: 'keys', line: `${branded.length} branded groups` },
    { id: 'brnkpi-champion', label: 'Highest BAR (group)', kind: 'keys', line: best ? `MAD ${fmt.mad(best.bar_mad)} · median of ${best.bar_hotels} hotels` : '' },
    { id: 'brnkpi-largest', label: 'Largest group', kind: 'keys', line: largest ? `${largest.total_keys.toLocaleString('en')} keys · ${largest.market_share_keys_pct.toFixed(1)}% of all keys` : '' },
  ], null);
}

function brandLogoOrInitials(bg, size) {
  if (LOCAL_BRAND_LOGOS[bg] || BRAND_CUSTOM_LOGOS[bg] || getBrandLogoUrl(bg)) {
    return getBrandLogoImg(bg, size, brandInitials(bg, size));
  }
  return brandInitials(bg, size);
}

function brandInitials(bg, size, gap = 0) {
  const initials = String(bg || '?').replace('Hotels', '').replace('Hotel', '').replace('Resorts', '').replace('International', '')
    .trim().split(/\s+/).slice(0, 2).map(w => w[0]).join('').toUpperCase();
  // a neutral tile (no colour-coded categories, docs/ui-standard.md)
  return initialsTile(initials, size, gap, 'var(--bg)', 'var(--text-2)');
}

// The group's BAR and Rooms RevPAR as on the Market Overview: the figure with its
// inline bar, the Limited data badge (under 3 hotels), or "—"
const brandsBarCell = (b, max) => b.bar_mad == null ? '<span class="cell-na">—</span>'
  : b.bar_limited ? limitedBadge(`${b.bar_hotels} hotel${b.bar_hotels === 1 ? '' : 's'} with ${KodoBar.meta().min_nights} priced nights; a group needs ${KodoBar.meta().min_hotels}.`)
  : `<span class="cell-num" data-tip="${escAttr(`Median of ${b.bar_hotels} hotels' BAR · ${b.bar_nights} priced nights`)}">${fmt.mad(b.bar_mad)}</span>${inlineBar(b.bar_mad, max, false)}`;
const brandsRevparCell = b => b.revpar_limited ? limitedBadge(`Rooms RevPAR (est.): fewer than ${KodoBar.meta().min_hotels} hotels with a BAR and ${KodoBar.meta().min_nights} priced coming nights.`)
  : b.avg_revpar == null ? '<span class="cell-na">—</span>' : `<span title="${EST_TIP}">${fmt.mad(b.avg_revpar)}</span>`;
const brandsPipeCell = b => b.pipeline_projects > 0
  ? `<button type="button" class="k-link brands-pipe" data-pipe-group="${escAttr(b.brand_group)}" title="Open the Pipeline filtered on ${escAttr(b.brand_group)}">${b.pipeline_projects} / ${b.pipeline_keys.toLocaleString('en')}</button>`
  : '<span class="cell-na">—</span>';

function renderBrandsCompTable(data) {
  const tbody = document.getElementById('brands-comp-tbody');
  if (!data.length) { tbody.innerHTML = '<tr><td colspan="8" class="k-empty">No brand group matches these filters.</td></tr>'; return; }
  const ok = brandsData.filter(b => b.bar_mad != null && !b.bar_limited);
  const maxBar = Math.max(0, ...ok.map(b => b.bar_mad));
  const maxShare = Math.max(0, ...brandsData.map(b => b.market_share_keys_pct || 0));
  const maxOcc = Math.max(0, ...brandsData.map(b => b.avg_occupancy || 0));
  tbody.innerHTML = data.map(b => `<tr data-brand-group="${escAttr(b.brand_group)}" tabindex="0">
      <td class="brands-name"><span class="k-brand">${getBrandLogoImg(b.brand_group, 20)}<span>${fmt.esc(b.brand_group)}</span></span>
        <span class="brands-name-m">${b.hotels} hotel${b.hotels !== 1 ? 's' : ''} · ${b.market_share_keys_pct.toFixed(1)}% of keys</span></td>
      <td class="num col-hide-mobile">${b.hotels}</td>
      <td class="num">${b.total_keys.toLocaleString('en')}</td>
      <td class="num cell-metric col-hide-mobile"><span class="cell-num">${b.market_share_keys_pct.toFixed(1)}%</span>${inlineBar(b.market_share_keys_pct, maxShare, false)}</td>
      <td class="num cell-metric">${brandsBarCell(b, maxBar)}</td>
      <td class="num cell-metric col-hide-mobile">${b.avg_occupancy == null ? '<span class="cell-na">—</span>' : `<span class="cell-num" title="${EST_TIP}">${fmt.pct(b.avg_occupancy)}</span>${inlineBar(b.avg_occupancy, maxOcc, true)}`}</td>
      <td class="num col-hide-mobile">${brandsRevparCell(b)}</td>
      <td class="num col-hide-mobile">${brandsPipeCell(b)}</td>
    </tr>`).join('');
  const m = KodoBar.meta();
  document.getElementById('brands-th-bar').dataset.tip = `BAR (published rate): the median of the group's hotels that have ${m.min_nights} or more priced past nights since 3 Nov 2026. Limited data under ${m.min_hotels} such hotels, "—" with none.`;
  document.getElementById('brands-th-revpar').dataset.tip = `Rooms RevPAR (est.): published price × estimated occupancy over the next 30 nights. Limited data under ${m.min_hotels} hotels with a BAR and ${m.min_nights} priced coming nights.`;
}

// Cards: the same figures in compact equal-height cards (no descriptions, no coloured pills)
function renderBrandsCards(data) {
  const grid = document.getElementById('brands-cards-grid');
  if (!data.length) { grid.innerHTML = '<p class="k-empty">No brand group matches these filters.</p>'; return; }
  const ok = brandsData.filter(b => b.bar_mad != null && !b.bar_limited);
  const maxBar = Math.max(0, ...ok.map(b => b.bar_mad));
  grid.innerHTML = data.map(b => `<div class="brn-card2" data-brand-group="${escAttr(b.brand_group)}" tabindex="0" role="link" aria-label="${escAttr(b.brand_group)}: open the brand page">
      <div class="brn-card2-head">${brandLogoOrInitials(b.brand_group, 32)}<div><div class="brn-card2-name">${fmt.esc(b.brand_group)}</div>
        <div class="brn-card2-sub">${b.hotels} hotel${b.hotels !== 1 ? 's' : ''} · ${b.total_keys.toLocaleString('en')} keys · ${b.market_share_keys_pct.toFixed(1)}%</div></div></div>
      <dl class="brn-card2-nums">
        <div><dt>BAR</dt><dd>${brandsBarCell(b, maxBar)}</dd></div>
        <div><dt>Occupancy (est.)</dt><dd>${b.avg_occupancy == null ? '<span class="cell-na">—</span>' : `<span title="${EST_TIP}">${fmt.pct(b.avg_occupancy)}</span>`}</dd></div>
        <div><dt>Rooms RevPAR (est.)</dt><dd>${brandsRevparCell(b)}</dd></div>
        <div><dt>Pipeline</dt><dd>${brandsPipeCell(b)}</dd></div>
      </dl>
    </div>`).join('');
}

// Pipeline cell: the Pipeline screen, filtered on the group
function openPipelineForGroup(bg) {
  _srchNavigateToScreen('pipeline');
  let tries = 0;
  const apply = () => {
    const sel = document.getElementById('pipe-group-filter');
    if (!pipelineData || sel.options.length < 2) { if (tries++ < 60) setTimeout(apply, 100); return; }
    const opt = [...sel.options].find(o => o.value === bg);
    if (opt) { sel.value = bg; pipelineState.group = bg; }
    else { pipelineState.q = bg; document.getElementById('pipe-search').value = bg; }
    applyPipelineFilter();
  };
  apply();
}

// ─── Brand detail ─────────────────────────────────────────────────

// Brand page: back, logo tile, name, one line; a Destination select that
// filters the page; four compact cards; About in three lines; the hotels
// table; the group's pipeline projects (linked to the Pipeline)
function showBrandDetail(brandGroup, prevScreen) {
  brandDetailPrevScreen = prevScreen || 'dashboard';
  brandDetailGroup = brandGroup;
  const backBtn = document.getElementById('brand-back-btn');
  backBtn.textContent = '← Back to ' + ({ brands: 'Brands', pipeline: 'Pipeline', hotel: 'Hotel', hotels: 'Hotels' }[brandDetailPrevScreen] || 'Dashboard');

  brandHotelsData = hotels.filter(h => h.brand_group === brandGroup
    || (brandGroup === 'Independent Hotels' && (h.brand_group === 'Independent' || h.brand_group === 'Independent Luxury')));
  const cities = [...new Set(brandHotelsData.map(h => h.city))].sort((a, b) => dn(a).localeCompare(dn(b)));

  document.getElementById('brand-detail-logo').innerHTML = getBrandLogoImg(brandGroup, 44);
  document.getElementById('brand-detail-name').textContent = brandGroup;
  const sel = document.getElementById('brand-dest-select');
  sel.replaceChildren(new Option('All destinations', ''), ...cities.map(c => new Option(dn(c), c)));
  sel.hidden = cities.length < 2;
  activeBrandCity = null;

  // Switch to the brand screen
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById('screen-brand').classList.add('active');
  scrollMainToTop();
  setSidebar('brand');

  // About: three lines, "Read more" opens the rest
  const description = BRAND_DESCRIPTIONS[brandGroup] || '';
  const about = document.getElementById('brand-about-slot');
  about.hidden = !description;
  document.getElementById('brand-about-text').textContent = description;
  about.classList.remove('is-open');
  const more = document.getElementById('brand-about-more');
  more.textContent = 'Read more'; more.setAttribute('aria-expanded', 'false');
  requestAnimationFrame(() => { const t = document.getElementById('brand-about-text'); more.hidden = t.scrollHeight <= t.clientHeight + 2; });

  brandState.col = 'name';
  brandState.dir = 1;
  renderBrandScope();
}

// Everything that follows the Destination select: line, cards, hotels, pipeline
function renderBrandScope() {
  const list = activeBrandCity ? brandHotelsData.filter(h => h.city === activeBrandCity) : brandHotelsData;
  const keysOf = h => h.under_renovation || h.seasonal_closure ? 0 : (h.keys || 0);
  const tk = list.reduce((s, h) => s + keysOf(h), 0);
  const nDest = new Set(list.map(h => h.city)).size;
  const owners = [...new Set(list.map(h => h.owner).filter(o => o && o !== 'Undisclosed'))];
  const parts = [`${list.length} hotel${list.length !== 1 ? 's' : ''}`, `${fmt.num(tk)} key${tk !== 1 ? 's' : ''}`,
    activeBrandCity ? dn(activeBrandCity) : `${nDest} destination${nDest !== 1 ? 's' : ''}`];
  if (owners.length === 1) parts.push(`owned by ${ownerText(list.find(h => h.owner === owners[0]))}`);
  document.getElementById('brand-detail-line').textContent = parts.join(' · ');

  document.getElementById('brand-bkpi-keys').querySelector('.kpi-value').textContent = fmt.num(tk);
  KodoPeriod.set('brand-bkpi-keys', KodoPeriod.today(), COUNT_TIP);
  Promise.resolve(KodoLive.cards({ occ: 'brand-bkpi-occ', rate: 'brand-bkpi-adr', revpar: 'brand-bkpi-revpar' }, list)).then(() => {
    const a = KodoLive.raw() ? KodoLive.agg(list) : null;
    compactKpiCards([
      { id: 'brand-bkpi-adr', label: 'BAR (median)', kind: 'adr' },
      { id: 'brand-bkpi-occ', label: 'Occupancy (est.)', kind: 'occ' },
      { id: 'brand-bkpi-revpar', label: 'Rooms RevPAR (est.)', kind: 'revpar' },
      { id: 'brand-bkpi-keys', label: 'Total keys', kind: 'keys', line: `${list.length} hotel${list.length !== 1 ? 's' : ''} · ${KodoPeriod.label(KodoPeriod.today())}` },
    ], a);
  });
  renderBrandHotelsTable();
  renderBrandPipeline();
}

// The group's pipeline projects (same group names as the Pipeline page);
// hidden when there are none or the plan has no Pipeline
async function renderBrandPipeline() {
  const card = document.getElementById('brand-pipe-card');
  const bg = brandDetailGroup;
  if (!pipelineData) {
    try {
      const r = await fetch('/api/pipeline');
      if (!r.ok) { card.hidden = true; return; }
      pipelineData = await r.json();
    } catch { card.hidden = true; return; }
  }
  if (bg !== brandDetailGroup) return;
  const rows = pipelineData.filter(p => pipeBrandGroup(p) === bg && (!activeBrandCity || p.city === activeBrandCity))
    .sort((a, b) => (a.expected_opening || 9999) - (b.expected_opening || 9999) || (a.name || '').localeCompare(b.name || ''));
  card.hidden = !rows.length;
  if (!rows.length) return;
  const keys = rows.reduce((s, p) => s + pipeNewKeys(p), 0);
  document.getElementById('brand-pipe-title').textContent = `Pipeline · ${rows.length} project${rows.length !== 1 ? 's' : ''}${keys ? ` · ${keys.toLocaleString('en')} new keys` : ''}`;
  document.getElementById('brand-pipe-tbody').innerHTML = rows.map(p => `<tr data-pipe-open tabindex="0" title="Open in Pipeline">
      <td><span class="brand-pipe-name">${fmt.esc(p.name)}</span>${pipeConversionLine(p)}</td>
      <td class="col-hide-mobile">${fmt.esc(dn(p.city || ''))}</td>
      <td>${pipeStagePill(p)}</td>
      <td class="num">${fmt.esc(String(pipeYear(p) === PIPE_NO_DATE ? 'TBA' : pipeYear(p)))}</td>
      <td class="num">${pipeKeysText(p)}</td>
    </tr>`).join('');
}

function renderBrandHotelsTable() {
  const { col, dir } = brandState;
  const filtered = activeBrandCity ? brandHotelsData.filter(h => h.city === activeBrandCity) : brandHotelsData;
  const val = h => col === 'status' ? hotelStatus(h) : col === 'city' ? dn(h.city || '') : h[col];
  const sorted = [...filtered].sort((a, b) => {
    const va = val(a), vb = val(b);
    if (BRAND_STR_COLS.has(col)) return dir * String(va ?? '').localeCompare(String(vb ?? '')) || a.name.localeCompare(b.name);
    if (va == null || vb == null) return (va == null) - (vb == null);
    return dir * (va - vb);
  });
  document.getElementById('brand-hotels-title').textContent =
    `Hotels · ${sorted.length}${activeBrandCity ? ' in ' + dn(activeBrandCity) : ''}`;
  const maxBar = Math.max(0, ...brandHotelsData.map(h => h.bar_mad).filter(v => v != null));
  const maxOcc = Math.max(0, ...brandHotelsData.map(h => h.occupancy).filter(v => v != null));
  document.getElementById('brand-hotels-tbody').innerHTML = sorted.map(h => {
    const out = h.under_renovation || h.seasonal_closure;
    const bar = h.bar_mad == null ? KodoBar.hotelCell(h) : `<span class="cell-num">${KodoBar.hotelCell(h)}</span>${inlineBar(h.bar_mad, maxBar, false)}`;
    const occ = out || h.occupancy == null
      ? `<span class="cell-na" title="${escAttr(out ? hotelStatusTip(h) : 'No estimate yet')}">—</span>`
      : `<span class="hotels-occ"><span class="cell-num" title="${EST_TIP}">${fmt.pct(h.occupancy)}</span>${destBadge(h.city)}</span>${inlineBar(h.occupancy, maxOcc, !isOfficial(h.city))}`;
    const tip = hotelStatusTip(h);
    return `<tr data-hid="${h.id}" tabindex="0">
      <td class="hotels-name"><span class="hotels-name-t">${fmt.esc(h.name)}</span><span class="hotels-name-m">${fmt.esc(dn(h.city))}${h.category ? ' · ' + fmt.esc(h.category) : ''}</span></td>
      <td class="col-hide-mobile">${fmt.esc(dn(h.city))}</td>
      <td class="col-hide-mobile">${fmt.esc(h.category || '—')}</td>
      <td class="num col-hide-mobile">${fmt.num(out ? h.keys_listed : h.keys)}</td>
      <td class="num cell-metric">${bar}</td>
      <td class="num cell-metric">${occ}</td>
      <td class="col-hide-mobile"><span class="hotels-status"${tip ? ` title="${escAttr(tip)}"` : ''}>${hotelStatus(h)}</span></td>
    </tr>`;
  }).join('');
  document.querySelectorAll('#brand-hotels-table th[data-bcol]').forEach(th => {
    if (th.dataset.bcol === col) th.setAttribute('aria-sort', dir === 1 ? 'ascending' : 'descending');
    else th.removeAttribute('aria-sort');
  });
}

// Brand page events: the Destination select, About, rows, pipeline
document.getElementById('brand-dest-select').addEventListener('change', e => {
  activeBrandCity = e.target.value || null;
  renderBrandScope();
});
document.getElementById('brand-about-more').addEventListener('click', e => {
  const about = document.getElementById('brand-about-slot');
  const open = about.classList.toggle('is-open');
  e.currentTarget.textContent = open ? 'Show less' : 'Read more';
  e.currentTarget.setAttribute('aria-expanded', String(open));
});
document.getElementById('brand-hotels-tbody').addEventListener('click', e => {
  if (e.target.closest('[data-tip], .kodo-badge')) return;
  const row = e.target.closest('tr[data-hid]');
  if (row) showHotelDetail(+row.dataset.hid);
});
document.getElementById('brand-pipe-open').addEventListener('click', () => openPipelineForGroup(brandDetailGroup));
document.getElementById('brand-pipe-tbody').addEventListener('click', e => { if (e.target.closest('tr[data-pipe-open]')) openPipelineForGroup(brandDetailGroup); });
document.getElementById('screen-brand').addEventListener('keydown', e => {
  if (!e.target.matches || !(e.key === 'Enter' || e.key === ' ')) return;
  if (e.target.matches('tr[data-hid]')) { e.preventDefault(); showHotelDetail(+e.target.dataset.hid); }
  else if (e.target.matches('tr[data-pipe-open]')) { e.preventDefault(); openPipelineForGroup(brandDetailGroup); }
});

// ─── Hotel detail ─────────────────────────────────────────────────

const OWNER_CONTEXT = {
  'Risma':        'Accor Morocco listed subsidiary (Bourse de Casablanca)',
  'Madaëf':       'CDG Group hospitality arm',
  'Royal Mansour': 'Royal Mansour Collection — Royal hospitality group',
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
  scrollMainToTop();

  // ── 1. Header: name, status and verified as neutral pills; one line with
  // the brand group (logo, linked to Brands), the destination (linked to the
  // Market Overview), the segment, the owner (linked to Owners) and the year opened
  document.getElementById('hotel-hd-name').textContent = h.name;
  const st = document.getElementById('hotel-hd-status');
  st.textContent = hotelStatus(h);
  st.title = hotelStatusTip(h);
  const verified = (h.data_quality || '').toLowerCase().startsWith('verified');
  document.getElementById('hotel-hd-dq').textContent = verified ? 'Verified' : 'Estimated';
  renderHotelHeadLine(h);

  // ── 2. Cards: label, one number, one short line; the rest in the "i"
  const setKv = (id, v) => document.getElementById(id).querySelector('.kpi-value').textContent = v;
  setKv('hkpi-detail-keys', fmt.num(h.under_renovation || h.seasonal_closure ? h.keys_listed : h.keys));
  KodoPeriod.set('hkpi-detail-keys', KodoPeriod.today(), COUNT_TIP);
  Promise.resolve(KodoLive.cards({ occ: 'hkpi-occ', rate: 'hkpi-adr', revpar: 'hkpi-revpar' }, [h])).then(() => compactHotelCards(h));

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
  KodoEvents.renderNext90(document.getElementById('hotel-events-next90'), h.city);

  // ── 9. One calendar: occupancy (est.) as the shade, BAR as the number ──
  renderRateCalendar(h.id);
}

function renderHotelHeadLine(h) {
  const el = document.getElementById('hotel-hd-sub');
  const parts = [brandGroupLink(h.brand_group, 18, 'hotel')];
  if (h.brand && h.brand !== h.brand_group && h.brand !== h.name) parts[0] = parts[0].replace('<span>' + fmt.esc(h.brand_group) + '</span>', `<span>${fmt.esc(h.brand_group)}</span><span class="hotel-hd-sub-brand">(${fmt.esc(h.brand)})</span>`);
  parts.push(`<button type="button" class="k-link" data-dest="${escAttr(h.city)}" title="Open ${escAttr(dn(h.city))} on the Market Overview">${fmt.esc(dn(h.city))}</button>`);
  if (h.category) parts.push(fmt.esc(h.category));
  if (h.owner && h.owner !== 'Undisclosed')
    parts.push(`Owner: <button type="button" class="k-link" data-owner="${escAttr(h.owner)}">${fmt.esc(h.owner)}</button>${h.owner_via ? ` (via ${fmt.esc(h.owner_via)})` : ''}`);
  if (h.year_opened) parts.push(`Opened ${h.year_opened}`);
  el.innerHTML = parts.map(x => `<span class="hotel-hd-part">${x}</span>`).join('<span class="hotel-hd-sep" aria-hidden="true">·</span>');
}
// Owner name -> its page on Owners (the owners list loads once)
async function openOwnerByName(name) {
  if (!ownersData) { try { ownersData = await fetch('/api/owners').then(r => r.ok ? r.json() : null); } catch { ownersData = null; } }
  const o = (ownersData || []).find(x => x.name === name) || (ownersData || []).find(x => fold(x.name) === fold(name));
  _srchNavigateToScreen('owners');
  if (o) showOwnerDetail(o.id);
}
document.getElementById('hotel-hd-sub').addEventListener('click', e => {
  const brand = e.target.closest('.k-brand-link');
  if (brand) { showBrandDetail(brand.dataset.brandGroup, 'hotel'); return; }
  const dest = e.target.closest('[data-dest]');
  if (dest) { _srchNavigateToScreen('dashboard'); selectCity(dest.dataset.dest); return; }
  const own = e.target.closest('[data-owner]');
  if (own) openOwnerByName(own.dataset.owner);
});

// The hotel's four cards in the Market Overview's form; the occupancy card
// carries the Official / Estimate badge (the calibration detail in its tooltip)
function compactHotelCards(h) {
  const L = (KodoLive.raw() || {}).hotels || {};
  const keysLine = h.under_renovation ? 'partly open, under renovation' : h.seasonal_closure ? CLOSED_NOTE.toLowerCase() : KodoPeriod.label(KodoPeriod.today());
  compactKpiCards([
    { id: 'hkpi-detail-keys', label: 'Keys', kind: 'keys', line: keysLine },
    { id: 'hkpi-adr', label: 'BAR', kind: 'adr' },
    { id: 'hkpi-occ', label: 'Occupancy (est.)', kind: 'occ', badge: h.under_renovation || h.seasonal_closure ? '' : destBadge(h.city) },
    { id: 'hkpi-revpar', label: 'Rooms RevPAR (est.)', kind: 'revpar' },
  ], null);
}

// Market positioning: BAR of every hotel in the city (observed since
// 3 Nov 2026), this hotel blue, the others grey
function renderHotelCityChart(h) {
  const cityHotels = hotels.filter(x => x.city === h.city && x.bar_mad != null).sort((a, b) => b.bar_mad - a.bar_mad);
  document.getElementById('hotel-ctx-sub').textContent = `BAR (published rate) · MAD · ${KodoBar.caption()}`;
  if (hotelCityChart) { hotelCityChart.destroy(); hotelCityChart = null; }
  if (!chartOrCollecting('chart-hotel-city', !cityHotels.length, `No hotel in ${h.city} has ${KodoBar.meta().min_nights} priced nights yet.`)) return;
  const p = KodoPalette.get();
  const labels = cityHotels.map(x => +x.id === +h.id ? `▶ ${x.name}` : x.name);
  const colors = cityHotels.map(x => +x.id === +h.id ? p.families.blue.dot : p.families.grey.dot);
  document.getElementById('hotel-city-chart-wrap').style.height = Math.max(200, cityHotels.length * 30 + 50) + 'px';
  const cfg = chartConfig(labels, cityHotels.map(x => x.bar_mad), ' MAD', colors, v => Math.round(v).toLocaleString('en'));
  cfg.options.plugins.tooltip.callbacks.label = ctx => `  BAR MAD ${Math.round(ctx.raw).toLocaleString('en')} · ${cityHotels[ctx.dataIndex].bar_nights} nights`;
  cfg.options.scales.y.ticks.callback = function (value) {
    const label = this.getLabelForValue(value);
    const max = this.chart.width < 520 ? 14 : 48;
    return label.length > max ? label.slice(0, max - 1).trimEnd() + '…' : label;
  };
  hotelCityChart = new Chart(document.getElementById('chart-hotel-city'), cfg);
}

// Segment benchmarks: this hotel against the other hotels of its segment in
// its city. BAR observed; occupancy a Kodo estimate (next 30 nights).
function renderHotelSegBench(h) {
  const peers = hotels.filter(x => x.city === h.city && x.category === h.category && +x.id !== +h.id);
  const bench  = document.getElementById('hotel-seg-bench');
  const ctxEl  = document.getElementById('hotel-bench-ctx');
  ctxEl.textContent = `${h.category} · ${h.city} average (${peers.length} peer${peers.length !== 1 ? 's' : ''})`;
  if (!peers.length) {
    bench.innerHTML = `<p class="hbench-no-peers">No comparable ${h.category} hotels in ${h.city}.</p>`;
    return;
  }
  const g = KodoBar.group(peers);
  const occPeers = peers.filter(x => x.occupancy != null && x.keys);
  const tk = occPeers.reduce((t, x) => t + x.keys, 0);
  const avgOcc = tk ? occPeers.reduce((t, x) => t + x.occupancy * x.keys, 0) / tk : null;
  const metrics = [
    { label: 'BAR (MAD)', sub: KodoBar.since(), mine: h.bar_mad, avg: KodoBar.shown(g) ? g.val : null,
      avgNote: g.val == null ? 'no peer priced yet' : g.limited ? `limited data (${g.n} peer${g.n === 1 ? '' : 's'})` : '',
      fmtVal: v => fmt.mad(v), fmtDiff: d => (d >= 0 ? '+' : '−') + 'MAD ' + fmt.mad(Math.abs(d)) },
    { label: 'Occupancy', sub: 'Kodo estimate · next 30 nights', mine: h.occupancy, avg: avgOcc, avgNote: '',
      fmtVal: v => fmt.pct(v), fmtDiff: d => (d >= 0 ? '+' : '') + (d * 100).toFixed(1) + ' pts' },
  ];
  bench.innerHTML = metrics.map(m => {
    const both = m.mine != null && m.avg != null;
    const top = Math.max(m.mine || 0, m.avg || 0) * 1.12 || 1;
    const w = v => v == null ? 0 : Math.round(v / top * 100);
    const diff = both ? m.mine - m.avg : null;
    const pos = diff != null && diff >= 0;
    return `<div class="hbench-row">
      <div class="hbench-label">${m.label}<span class="hbench-label-sub">${m.sub}</span></div>
      <div class="hbench-bars">
        <div class="hbench-bar-row">
          <span class="hbench-bar-lbl">This hotel</span>
          <div class="hbench-bar-track"><div class="hbench-bar-fill accent" style="width:${w(m.mine)}%"></div></div>
          <span class="hbench-val">${m.mine == null ? '—' : m.fmtVal(m.mine)}</span>
        </div>
        <div class="hbench-bar-row">
          <span class="hbench-bar-lbl">Peers avg</span>
          <div class="hbench-bar-track"><div class="hbench-bar-fill muted" style="width:${w(m.avg)}%"></div></div>
          <span class="hbench-val">${m.avg == null ? (m.avgNote || '—') : m.fmtVal(m.avg)}</span>
        </div>
      </div>
      <span class="hbench-diff ${pos ? 'up' : 'down'}">${diff == null ? '' : `<span class="pill--${pos ? 'green' : 'red'}">${m.fmtDiff(diff)}</span>`}</span>
    </div>`;
  }).join('');
}

async function renderHotelPipeline(h) {
  const content = document.getElementById('hotel-pipe-content');
  if (!pipelineData) {
    showLoading(content);
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

  const totalKeys = cityPipe.reduce((s, p) => s + pipeNewKeys(p), 0);
  const years     = cityPipe.filter(p => !p.conversion).map(p => p.expected_opening).filter(Boolean);
  const lastYear  = years.length ? Math.max(...years) : null;
  const items = cityPipe.map(p => {
    const conv = !p.conversion ? ''
      : String(p.converts_hotel_id) === String(h.id) ? ' · conversion of this hotel'
      : ` · conversion of ${fmt.esc(p.converts_hotel_name || 'an operating hotel')}`;
    return `
    <div class="hpipe-item">
      <div class="hpipe-item-name">${fmt.esc(p.name)}</div>
      <span class="hpipe-item-meta">${pipeBrandHtml(p, 14)} · ${p.keys || 'TBC'} keys · ${fmt.esc(pipeYear(p))}${conv}</span>
      ${pipeStagePill(p)}
    </div>`;
  }).join('');
  const undated = cityPipe.some(p => !p.expected_opening && !p.conversion);
  const when = lastYear ? ` by ${lastYear}${undated ? ', plus projects with no date announced' : ''}` : '';
  const summary = totalKeys
    ? `${totalKeys.toLocaleString('en')} new keys entering ${fmt.esc(h.city)}${when}`
    : cityPipe.every(p => p.conversion)
      ? `No new rooms announced in ${fmt.esc(h.city)}: ${cityPipe.length === 1 ? 'one conversion' : cityPipe.length + ' conversions'} of an existing hotel`
      : `Projects in ${fmt.esc(h.city)} with no room count announced yet`;

  content.innerHTML = `
    <p class="hpipe-summary">${summary}</p>
    <div class="hpipe-list">${items}</div>`;
}

function renderOwnerSection(h) {
  const section = document.getElementById('hotel-owner-section');
  if (!h.owner || h.owner === 'Undisclosed') {
    section.style.display = 'none';
    return;
  }
  section.style.display = '';
  const ownerName = document.getElementById('hotel-owner-name');
  ownerName.innerHTML = getOwnerLogoImg(h.owner, 32) + fmt.esc(h.owner);

  let ctx = h.owner_via ? `via ${h.owner_via}` : '';
  for (const [key, val] of Object.entries(OWNER_CONTEXT)) {
    if (!ctx && h.owner.includes(key)) { ctx = val; break; }
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
  live_dataforseo: 'src-live-google',
  live_brand:      'src-live-brand',
  live_booking:    'src-live-booking',
  manual_override: 'src-manual-override',
  estimated:       'src-estimated',
  unavailable:     'src-unavailable',
};

const SOURCE_LABEL = {
  live_dataforseo: 'Published rates',
  live_brand:      'Brand Direct',
  live_booking:    'Published rates',
  manual_override: 'Manual Override',
  estimated:       'Estimated',
  unavailable:     'Unavailable',
};

// YYYY-MM-DD in the visitor's own timezone (toISOString() is UTC, which
// shifts every calendar cell by a day for part of the day east/west of UTC)
function localIsoDate(d) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

// ── Calendar tooltip (shared by every calendar) ─────────────────────
// A cell carries its tooltip as data: calTipAttrs(date, rows) where each
// row is [label, value] or [label, value, note]. One tooltip element on
// <body> shows it on hover, keyboard focus and tap, placed above the cell
// (below when there's no room) and kept inside the viewport.
const calTipEsc = s => String(s).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
function calTipAttrs(date, rows) {
  return ` tabindex="0" data-cal-tip="${calTipEsc(JSON.stringify({ date, rows }))}"`;
}

const CalTip = (() => {
  let el = null, cell = null, pinned = false, lastPointer = 'mouse';
  function node() {
    if (!el) {
      el = document.createElement('div');
      el.className = 'cal-tip'; el.id = 'cal-tip'; el.setAttribute('role', 'tooltip'); el.hidden = true;
      document.body.appendChild(el);
    }
    return el;
  }
  function show(target, pin) {
    let tip;
    try { tip = JSON.parse(target.dataset.calTip); } catch { return; }
    const t = node();
    const date = document.createElement('div');
    date.className = 'cal-tip-date'; date.textContent = tip.date;
    const grid = document.createElement('div');
    grid.className = 'cal-tip-grid';
    t.replaceChildren(date, grid);
    (tip.rows || []).forEach(([label, value, note]) => {
      const hasValue = value != null && value !== '';
      const l = document.createElement('span');
      l.className = 'cal-tip-label' + (hasValue ? '' : ' cal-tip-label--wide'); l.textContent = label;
      grid.appendChild(l);
      if (hasValue) {
        const v = document.createElement('span'); v.className = 'cal-tip-value'; v.textContent = value;
        grid.appendChild(v);
      }
      if (note) {
        const n = document.createElement('span'); n.className = 'cal-tip-note'; n.textContent = note;
        grid.appendChild(n);
      }
    });
    if (!grid.childElementCount) grid.remove();
    if (cell && cell !== target) cell.removeAttribute('aria-describedby');
    cell = target; pinned = !!pin;
    cell.setAttribute('aria-describedby', 'cal-tip');
    t.hidden = false;
    place();
  }
  function place() {
    if (!el || el.hidden || !cell) return;
    const GAP = 8, EDGE = 8;
    const c = cell.getBoundingClientRect();
    el.style.left = '0px'; el.style.top = '0px';   // measure at full width, not squeezed by the last position
    const w = el.offsetWidth, h = el.offsetHeight;
    const vw = document.documentElement.clientWidth, vh = window.innerHeight;
    // Above the cell when it fits; else below; else whichever side has more room
    let top = c.top - GAP - h;
    if (top < EDGE) top = (c.bottom + GAP + h <= vh - EDGE || vh - c.bottom > c.top) ? c.bottom + GAP : top;
    top = Math.max(EDGE, Math.min(top, vh - EDGE - h));
    let left = c.left + c.width / 2 - w / 2;
    left = Math.max(EDGE, Math.min(left, vw - EDGE - w));
    el.style.left = Math.round(left) + 'px';
    el.style.top = Math.round(top) + 'px';
  }
  function hide() {
    if (el) el.hidden = true;
    if (cell) cell.removeAttribute('aria-describedby');
    cell = null; pinned = false;
  }
  const target = e => e.target.closest && e.target.closest('[data-cal-tip]');
  document.addEventListener('pointerdown', e => { lastPointer = e.pointerType || 'mouse'; }, true);
  document.addEventListener('mouseover', e => {
    if (lastPointer !== 'mouse') return;
    const t = target(e);
    if (t && t !== cell) show(t);
  });
  document.addEventListener('mouseout', e => {
    if (lastPointer !== 'mouse' || pinned || !cell) return;
    const t = target(e);
    if (t === cell && !cell.contains(e.relatedTarget)) hide();
  });
  document.addEventListener('focusin', e => { const t = target(e); if (t) show(t); else if (cell) hide(); });
  document.addEventListener('focusout', e => { if (target(e) === cell && !pinned) hide(); });
  document.addEventListener('click', e => {
    const t = target(e);
    if (lastPointer === 'mouse') return;
    if (!t) { if (cell) hide(); return; }
    if (t === cell && pinned) hide(); else show(t, true);
  });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && cell) hide(); });
  window.addEventListener('scroll', () => { if (cell) (pinned || document.activeElement === cell) ? place() : hide(); }, true);
  window.addEventListener('resize', () => place());
  return { hide };
})();

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

// ── Hotel rate calendar: "Next 30 nights", or a past month showing each
// night's last published rate (the last price seen before the night) ──
const HR_MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];
const hrState = { hotelId: null, view: 'next', first: null, req: 0, shade: 'occ', next: null };
const hrMonthKey = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
const hrMonthName = k => `${HR_MONTHS[+k.slice(5) - 1]} ${k.slice(0, 4)}`;
const hrShift = (k, n) => { const d = new Date(+k.slice(0, 4), +k.slice(5) - 1 + n, 1); return hrMonthKey(d); };

// The hotel page's one calendar. Next 30 nights: each night's date, its BAR
// (the latest published price) as the number and the occupancy estimate as
// the shade (greyscale, darker = busier), or the BAR as the shade on
// request. Past months: each night's last published rate (BAR shade only).
// Nights closed for the season read "Closed".
async function renderRateCalendar(hotelId) {
  hrState.hotelId = hotelId; hrState.view = 'next'; hrState.first = null; hrState.next = null;
  return hrRender();
}
function hrNav() {
  const cur = hrMonthKey(new Date()), v = hrState.view;
  document.getElementById('hrate-period').textContent = v === 'next' ? 'Next 30 nights' : hrMonthName(v);
  document.getElementById('hrate-next').disabled = v === 'next';
  const prev = v === 'next' ? cur : hrShift(v, -1);
  document.getElementById('hrate-prev').disabled = !!hrState.first && prev < hrState.first && v !== 'next';
  document.getElementById('hrate-prev').setAttribute('aria-label', `Show ${hrMonthName(prev)}: last published rates`);
  document.getElementById('hrate-next').setAttribute('aria-label', v === 'next' ? 'Later' : (hrShift(v, 1) > cur ? 'Show the next 30 nights' : `Show ${hrMonthName(hrShift(v, 1))}`));
  // past months have published rates only: the shade is the BAR
  const occBtn = document.querySelector('#hcal-shade [data-shade="occ"]');
  occBtn.disabled = v !== 'next';
  occBtn.title = v === 'next' ? '' : 'Past months have published rates only';
  hrSyncShade();
}
const hrShadeNow = () => hrState.view === 'next' ? hrState.shade : 'bar';
function hrSyncShade() {
  document.querySelectorAll('#hcal-shade [data-shade]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.shade === hrShadeNow())));
}
function hrRender() {
  hrNav();
  return hrState.view === 'next' ? renderCalNext(hrState.hotelId) : renderRatePast(hrState.hotelId, hrState.view);
}
document.getElementById('hrate-prev')?.addEventListener('click', () => {
  hrState.view = hrState.view === 'next' ? hrMonthKey(new Date()) : hrShift(hrState.view, -1); hrRender();
});
document.getElementById('hrate-next')?.addEventListener('click', () => {
  if (hrState.view === 'next') return;
  const n = hrShift(hrState.view, 1);
  hrState.view = n > hrMonthKey(new Date()) ? 'next' : n; hrRender();
});
document.getElementById('hcal-shade')?.addEventListener('click', e => {
  const b = e.target.closest('[data-shade]');
  if (!b || b.disabled) return;
  hrState.shade = b.dataset.shade;
  hrSyncShade();
  if (hrState.view === 'next' && hrState.next) drawCalNext();
});

// Shade levels 0–3 (greyscale): occupancy in four bands; BAR from the
// lowest to the highest price shown (this hotel, these nights)
const HCAL_OCC_BANDS = ['under 40%', '40–60%', '60–80%', '80% and over'];
const hcalOccLevel = occ => occ >= 80 ? 3 : occ >= 60 ? 2 : occ >= 40 ? 1 : 0;
function hcalBarLevels(values) {
  const v = values.filter(x => x != null);
  const lo = Math.min(...v), hi = Math.max(...v);
  return x => x == null ? null : hi === lo ? 1 : Math.min(3, Math.floor((x - lo) / (hi - lo) * 4));
}
const hcalSw = (cls, label) => `<span class="hcal-leg-item"><span class="hcal-sw ${cls}" aria-hidden="true"></span>${label}</span>`;
const HCAL_LEG_EVENT = '<span class="hcal-leg-item"><span class="hcal-leg-ev" aria-hidden="true"></span>Event</span>';
function hcalLegend(shade, extra) {
  const sw = shade === 'occ'
    ? HCAL_OCC_BANDS.map((b, i) => hcalSw('hcal-l' + i, i === 0 ? 'Occupancy (est.) ' + b : b)).join('')
    : hcalSw('hcal-l0', 'Lower BAR') + hcalSw('hcal-l1', '') + hcalSw('hcal-l2', '') + hcalSw('hcal-l3', 'Higher BAR (this hotel, these nights)');
  return sw + extra.join('') + HCAL_LEG_EVENT;
}
const DAYS3 = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];

async function renderRatePast(hotelId, month) {
  const calEl = document.getElementById('hrate-calendar');
  const req = ++hrState.req;
  document.getElementById('hcal-badge').innerHTML = '<span class="k-pill k-pill--muted">Past nights</span>';
  document.getElementById('hcal-note').innerHTML = 'Last published rate: the last price seen before each night.';
  calEl.innerHTML = '<div class="bar-cal-loading">Loading past rates…</div>';
  let d;
  try { d = await (await fetch(`/api/rates/past?hotel_id=${encodeURIComponent(hotelId)}&month=${month}`)).json(); }
  catch { calEl.innerHTML = '<div class="bar-cal-loading">Past rates unavailable</div>'; return; }
  if (req !== hrState.req) return;
  hrState.first = d.first_month || month;
  hrNav();
  const byNight = Object.fromEntries((d.nights || []).map(n => [n.night, n]));
  const total = new Date(+month.slice(0, 4), +month.slice(5), 0).getDate();
  const level = hcalBarLevels((d.nights || []).filter(n => n.night < d.today).map(n => n.rate_mad == null ? null : +n.rate_mad));
  let html = '';
  for (let day = 1; day <= total; day++) {
    const dt = new Date(+month.slice(0, 4), +month.slice(5) - 1, day), iso = localIsoDate(dt);
    const n = byNight[iso], dn = `${DAYS3[dt.getDay()]} ${day}`;
    if (iso >= d.today) {
      html += `<div class="hcal-day hcal-none"${calTipAttrs(iso, [['Upcoming night: see Next 30 nights']])}><div class="hcal-dn">${dn}</div><div class="hcal-bar">·</div></div>`;
    } else if (!n || n.rate_mad == null) {
      html += `<div class="hcal-day hcal-none"${calTipAttrs(iso, [['No price collected before this night']])}><div class="hcal-dn">${dn}</div><div class="hcal-bar">—</div></div>`;
    } else {
      const tip = calTipAttrs(iso, [['Last published rate', fmtMadLong(n.rate_mad)],
        ['Collected', `${KodoPeriod.day(n.collected_on)} · ${n.days_before} ${n.days_before === 1 ? 'day' : 'days'} before`],
        ['Source', SOURCE_LABEL[n.source] || n.source]]);
      html += `<div class="hcal-day hcal-l${level(+n.rate_mad)}"${tip}><div class="hcal-dn">${dn}</div><div class="hcal-bar">${fmtMadShort(n.rate_mad)}</div></div>`;
    }
  }
  calEl.innerHTML = html;
  document.getElementById('hrate-legend').innerHTML = hcalLegend('bar', [hcalSw('hcal-none', 'No price collected')]);
  KodoEvents.markCells(calEl, (hotels.find(x => +x.id === +hotelId) || {}).city);
}

async function renderCalNext(hotelId) {
  const calEl = document.getElementById('hrate-calendar');
  const req = ++hrState.req;
  calEl.innerHTML = '<div class="bar-cal-loading">Loading…</div>';
  const get = url => fetch(url).then(r => r.ok ? r.json() : null).catch(() => null);
  const [rates, occ] = await Promise.all([get(`/api/rates?hotel_id=${hotelId}&days=35`), get(`/api/occupancy/${hotelId}`)]);
  if (req !== hrState.req) return;
  hrState.next = { rates: rates || {}, occ: occ || {}, hotelId, ok: !!(rates || occ) };
  if (!rates && !occ) { calEl.innerHTML = '<div class="bar-cal-loading">Calendar unavailable</div>'; return; }
  drawCalNext();
  renderCalAverages(occ);
}

function drawCalNext() {
  const { rates: data, occ, hotelId } = hrState.next;
  const calEl = document.getElementById('hrate-calendar');
  const shade = hrShadeNow();
  const h = hotels.find(x => +x.id === +hotelId) || {};

  // stay_date → the latest price observed for each night (on the same scrape
  // day the more trusted source wins, as in rates_store.py)
  const priority = {'live_dataforseo':5,'live_brand':5,'manual_override':4,'live_booking':3,'estimated':1,'unavailable':0};
  const later = (a, b) => a.scrape_date !== b.scrape_date ? a.scrape_date > b.scrape_date : (priority[a.source]||0) > (priority[b.source]||0);
  const rateMap = {};
  for (const r of (data.rates || [])) if (!rateMap[r.stay_date] || later(r, rateMap[r.stay_date])) rateMap[r.stay_date] = r;
  const estMap = {};
  for (const e of (occ.estimates || [])) estMap[e.date] = e;
  const closedSet = new Set(occ.closed_nights || []);    // closed for the season (no bookable rate)

  const today = new Date();
  const todayIso = data.today || localIsoDate(today);
  const ageDays = sd => Math.round((Date.parse(todayIso) - Date.parse(String(sd).slice(0, 10))) / 86400000);
  const nights = [];
  for (let i = 1; i <= 30; i++) {
    const d = new Date(today); d.setDate(today.getDate() + i);
    const iso = localIsoDate(d), r = rateMap[iso] || null, e = estMap[iso] || null;
    nights.push({ d, iso, r, e, rate: r && r.rate_mad ? +r.rate_mad : null, occ: e ? +e.estimated_occupancy : null, shut: !e && closedSet.has(iso) });
  }
  const barLevel = hcalBarLevels(nights.map(n => n.rate));
  let stale = false, noEst = false, noRate = false;
  calEl.innerHTML = nights.map(n => {
    const lvl = shade === 'occ' ? (n.occ == null ? null : hcalOccLevel(n.occ)) : barLevel(n.rate);
    const old = n.rate != null && ageDays(n.r.scrape_date) > RATE_STALE_DAYS;
    if (old) stale = true;
    if (n.occ == null && !n.shut) noEst = true;
    if (n.rate == null) noRate = true;
    const rows = [];
    let why = '';                                       // an empty night says why, in the cell
    if (n.rate != null) {
      const age = ageDays(n.r.scrape_date);
      rows.push(['BAR', fmtMadLong(n.rate)], ['Seen', `${seenAgo(age)} (${KodoPeriod.day(n.r.scrape_date)})`], ['Source', SOURCE_LABEL[n.r.source] || n.r.source]);
      if (old) rows.push(['', 'Seen over a week ago: it may have changed']);
    } else {
      const [txt, reason] = emptyNightLabel(data.lookup, n.iso);
      why = txt;
      rows.push([txt, reason]);
    }
    if (n.e) rows.push(['Occupancy (est.)', occRange(n.e)], ['Price coverage', COVERAGE_LABEL[occCoverage(n.e)] || occCoverage(n.e)]);
    else if (n.shut) rows.push([CLOSED_LABEL, CLOSED_NOTE]);
    else rows.push(['Occupancy (est.)', 'no estimate for this night']);
    const cls = n.shut ? 'hcal-closed' : lvl == null ? 'hcal-none' : 'hcal-l' + lvl;
    return `<div class="hcal-day ${cls}"${calTipAttrs(n.iso, rows)}>
      <div class="hcal-dn">${DAYS3[n.d.getDay()]} ${n.d.getDate()}</div>
      <div class="hcal-bar${old ? ' hcal-stale' : ''}${n.rate == null && !n.shut ? ' hcal-why' : ''}">${n.shut && n.rate == null ? 'Closed' : n.rate != null ? fmtMadShort(n.rate) : `<span class="hcal-why-l">${why}</span><span class="hcal-why-s" aria-hidden="true">—</span>`}</div>
      <div class="hcal-occ">${n.occ != null ? Math.round(n.occ) + '%' : n.shut ? '' : '—'}</div>
    </div>`;
  }).join('');

  const extra = [];
  if (shade === 'occ' && noEst) extra.push(hcalSw('hcal-none', 'No estimate'));
  if (shade === 'bar' && noRate) extra.push(hcalSw('hcal-none', 'No price: reason in the cell'));
  if (closedSet.size) extra.push(hcalSw('hcal-closed', CLOSED_LABEL));
  if (stale) extra.push('<span class="hcal-leg-item"><span class="hcal-stale">1.2k</span>&nbsp;price seen over a week ago</span>');
  document.getElementById('hrate-legend').innerHTML = hcalLegend(shade, extra);

  // the occupancy basis: Official / Estimate, the detail in the tooltip
  const allShut = closedSet.size && !(occ.estimates || []).some(e => e.date > localIsoDate(today));
  const cc = occ.price_coverage_counts || {};
  const nDays = (cc.full || 0) + (cc.partial || 0) + (cc.none || 0);
  const covLabel = ['full', 'partial', 'none'].find(k => nDays && (cc[k] || 0) > nDays / 2) || (nDays ? 'mixed' : '');
  const detail = ['Occupancy: modelled, not measured', occ.occ_basis, occ.model_run_date && `model run ${KodoPeriod.day(occ.model_run_date)}`,
    covLabel && `price coverage ${covLabel}`, closedSet.size && !allShut && `${CLOSED_NOTE}: closed on ${closedSet.size} of the next 30 nights`].filter(Boolean).join(' · ');
  document.getElementById('hcal-badge').innerHTML = occ.under_renovation ? `<span class="k-pill k-pill--muted">${RENOVATION_LABEL}</span>`
    : allShut ? `<span class="k-pill k-pill--muted" title="${escAttr(CLOSED_NOTE + ': no occupancy or Rooms RevPAR estimate for the next 30 nights')}">${CLOSED_LABEL}</span>`
    : occ.calibrated ? badgeHtml('official', `${DEST_BADGE_TIP.official} ${detail}.`) : badgeHtml('estimate', `Kodo estimate. ${detail}.`);

  // when the prices were last collected: one quiet line
  document.getElementById('hcal-note').textContent = data.last_live
    ? (data.live_stale ? `Last live rates: ${KodoPeriod.day(data.last_live)} · not updated since` : `Prices last collected ${KodoPeriod.day(data.last_live)} · updated nightly`)
    : ((data.rates || []).length ? 'Manual prices only · no live rates collected yet' : '');
  KodoEvents.markCells(calEl, h.city);
}

// 30-day averages and price coverage: one quiet line, the detail in its "i"
function renderCalAverages(data) {
  const line = document.getElementById('hotel-cal-averages');
  if (!data || data.avg_occupancy_30d == null) { line.hidden = true; return; }   // closed, under renovation: not the previous hotel's
  const cc = data.price_coverage_counts || {};
  const range = data.avg_low_30d != null && data.avg_high_30d != null ? ` (range ${data.avg_low_30d}–${data.avg_high_30d}%)` : '';
  const rRange = data.avg_revpar_low_30d != null && data.avg_revpar_high_30d != null ? ` (range ${Math.round(+data.avg_revpar_low_30d).toLocaleString()}–${Math.round(+data.avg_revpar_high_30d).toLocaleString()})` : '';
  document.getElementById('hcal-avg-bar-text').textContent = `Next 30 nights on average: occupancy (est.) ${data.avg_occupancy_30d}%`
    + (data.avg_revpar_30d ? ` · Rooms RevPAR (est.) MAD ${Math.round(+data.avg_revpar_30d).toLocaleString()}` : '');
  const tip = `Occupancy (Kodo estimate) ${data.avg_occupancy_30d}%${range}.`
    + (data.avg_revpar_30d ? ` Rooms RevPAR (est.: BAR × modelled occupancy) MAD ${Math.round(+data.avg_revpar_30d).toLocaleString()}${rRange}.` : '')
    + ` Price coverage: full ${cc.full ?? 0} days · partial ${cc.partial ?? 0} · none ${cc.none ?? 0}; it describes how many recent published prices we have for the hotel, not how accurate the estimate is.`;
  const i = document.getElementById('hcal-avg-info');
  i.dataset.tip = tip;
  i.setAttribute('aria-label', 'About these averages: ' + tip);
  line.hidden = false;
}

const RATE_STALE_DAYS = 7;          // a price seen longer ago than this looks less certain
// Why a night of the next 30 has no price, from the hotel's lookup in the
// latest nightly run: [cell label, tooltip text]. Never "sold out": a
// missing price does not say why.
function emptyNightLabel(lookup, iso) {
  const st = lookup && lookup.status;
  if (!st || st === 'no_id') return ['Not tracked yet', 'This hotel\u2019s published rates are not collected yet'];
  if (st === 'ok') {
    return lookup.window_start && (iso < lookup.window_start || iso > lookup.window_end)
      ? ['Not checked yet', 'This night is asked for in the next nightly run']
      : ['No rate published', 'Asked for in the latest nightly run: no published rate for this night'];
  }
  return ['Lookup failed', 'The latest nightly lookup for this hotel did not return its rates'];
}
function seenAgo(days) {
  return days <= 0 ? 'today' : days === 1 ? '1 day ago' : `${days} days ago`;
}

function fmMad(n) {
  if (!n) return '—';
  n = +n;
  if (n >= 1_000_000_000) return `MAD ${(n/1e9).toFixed(1)}B`;
  if (n >= 1_000_000)     return `MAD ${(n/1e6).toFixed(1)}M`;
  return `MAD ${Math.round(n).toLocaleString()}`;
}

// Price coverage of a stored night (full | partial | none); older rows
// only carry the former confidence level (high | medium | low)
const COVERAGE_LABEL = { full: 'Full', partial: 'Partial', none: 'None', mixed: 'Mixed' };   // tooltip values
function occCoverage(e) {
  return e.price_coverage || ({ high: 'full', medium: 'partial' })[e.confidence] || 'none';
}
// "62–74%" when the model gives a range, else the single value
function occRange(e) {
  const mid = e.mid ?? e.estimated_occupancy;
  return e.low != null && e.high != null ? `${Math.round(e.low)}–${Math.round(e.high)}%` : `${Math.round(+mid)}%`;
}


// ─── Map ──────────────────────────────────────────────────────────

function markerRadius(h) {
  return Math.max(8, Math.sqrt(h.keys) * 0.78);
}

function popupHTML(h) {
  return `
    <div class="hiq-popup">
      <button class="hiq-popup-name-btn" onclick="showHotelDetail(${h.id})">${fmt.esc(h.name)}</button>
      <div class="hiq-popup-meta">${fmt.esc(h.brand)} · ${getSegmentBadgeHtml(h.category)}${h.year_opened ? ` · ${h.year_opened}` : ''}</div>
      <div class="hiq-popup-grid">
        <div class="hiq-popup-stat">
          <div class="hiq-popup-stat-val">${hotelRooms(h)}</div>
          <div class="hiq-popup-stat-lbl">Keys</div>
        </div>
        <div class="hiq-popup-stat">
          <div class="hiq-popup-stat-val">${KodoBar.hotelCell(h)}</div>
          <div class="hiq-popup-stat-lbl">BAR (MAD)</div>
        </div>
        <div class="hiq-popup-stat" title="${EST_TIP}">
          <div class="hiq-popup-stat-val">${hotelOcc(h)}</div>
          <div class="hiq-popup-stat-lbl">Occ · Kodo est.</div>
        </div>
        <div class="hiq-popup-stat" title="${EST_TIP}">
          <div class="hiq-popup-stat-val">${fmt.mad(h.revpar_mad)}</div>
          <div class="hiq-popup-stat-lbl">Rooms RevPAR (est.)</div>
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
  if (pipelineInited && !googlePipelineMap) initPipelineMap();
}
// Defensive: guarantee this is reachable as a global even if this file is
// ever wrapped/bundled in a way that stops top-level functions from
// attaching themselves to window automatically.
window.initGoogleMaps = initGoogleMaps;

function swapMapTheme(mode) {
  const styles = gmapStyles();
  if (googleMap)         { googleMap.setOptions({ styles }); updateMapMarkers(); }
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
      styles: gmapStyles(),
    });

    updateMapMarkers();
  } catch (e) {
    console.error('Google Maps init failed:', e);
  }
}

// One dot per city (sized by matching hotel count) instead of one dot per
// hotel. Rebuilt whenever the city or segment filter changes, since a
// filter change can shrink a city's count and therefore its dot size.
let selectedCityEntry = null; // {marker, city, hotels, count} — tracks the open panel's dot so it stays highlighted

function cityDotIcon(count, highlighted) {
  const size = count <= 3 ? 8 : count <= 8 ? 12 : count <= 15 ? 16 : 20;
  return {
    path:        google.maps.SymbolPath.CIRCLE,
    scale:       size / 2,
    fillColor:   highlighted ? KodoPalette.get().families.blue.dot : KodoPalette.get().families.grey.dot,
    fillOpacity: 1,
    strokeColor: KodoPalette.get().bg,
    strokeWeight: 1.5,
  };
}

function updateMapMarkers() {
  if (!googleMap) return;

  hotelMarkers.forEach(({ marker }) => marker.setMap(null));
  hotelMarkers = [];
  selectedCityEntry = null;
  const existingPanel = document.getElementById('map-city-panel');
  if (existingPanel) existingPanel.remove();

  const filtered = hotels.filter(h =>
    (state.city   === 'all' || h.city     === state.city) &&
    (state.mapSeg === 'all' || h.category === state.mapSeg)
  );

  const hotelsByCity = {};
  filtered.forEach(h => {
    if (h.lat == null || h.lng == null) return;
    const city = h.city;
    if (!city) return;
    if (!hotelsByCity[city]) hotelsByCity[city] = { hotels: [], latSum: 0, lngSum: 0 };
    hotelsByCity[city].hotels.push(h);
    hotelsByCity[city].latSum += h.lat;
    hotelsByCity[city].lngSum += h.lng;
  });

  Object.entries(hotelsByCity).forEach(([city, data]) => {
    const count = data.hotels.length;
    const marker = new google.maps.Marker({
      position: { lat: data.latSum / count, lng: data.lngSum / count },
      map:      googleMap,
      icon:     cityDotIcon(count, false),
      title:    `${city} — ${count} hotel${count !== 1 ? 's' : ''}`,
    });
    const entry = { marker, city, hotels: data.hotels, count };

    marker.addListener('mouseover', () => {
      if (selectedCityEntry !== entry) marker.setIcon(cityDotIcon(count, true));
    });
    marker.addListener('mouseout', () => {
      if (selectedCityEntry !== entry) marker.setIcon(cityDotIcon(count, false));
    });
    marker.addListener('click', () => {
      if (selectedCityEntry && selectedCityEntry !== entry) {
        selectedCityEntry.marker.setIcon(cityDotIcon(selectedCityEntry.count, false));
      }
      selectedCityEntry = entry;
      marker.setIcon(cityDotIcon(count, true));
      showCityPanel(city, data.hotels);
    });

    hotelMarkers.push(entry);
  });

  const countEl = document.getElementById('map-count');
  if (countEl) countEl.textContent = filtered.length + ' hotel' + (filtered.length !== 1 ? 's' : '');
}

function showCityPanel(city, cityHotels) {
  const existing = document.getElementById('map-city-panel');
  if (existing) existing.remove();

  const panel = document.createElement('div');
  panel.id = 'map-city-panel';
  panel.className = 'map-city-panel';

  const hotelRows = cityHotels
    .slice()
    .sort((a, b) => b.revpar_mad - a.revpar_mad)
    .map(h => `
      <div class="map-city-panel-row" onclick="showHotelDetail(${h.id})">
        <div class="map-city-panel-row-name">${fmt.esc(h.name)}</div>
        <div class="map-city-panel-row-meta">${fmt.esc(h.brand || '')} · ${h.under_renovation ? `${h.keys_listed || ''} rooms, partly open, under renovation` : h.seasonal_closure ? `${h.keys_listed || ''} rooms, ${CLOSED_NOTE.toLowerCase()}` : `${h.keys || ''} rooms`}</div>
      </div>
    `).join('');

  panel.innerHTML = `
    <div class="map-city-panel-header">
      <div>
        <div class="map-city-panel-count">${cityHotels.length} Hotel${cityHotels.length !== 1 ? 's' : ''}</div>
        <div class="map-city-panel-city">${fmt.esc(city)}</div>
      </div>
      <button class="map-city-panel-close" onclick="document.getElementById('map-city-panel').remove(); if (selectedCityEntry) { selectedCityEntry.marker.setIcon(cityDotIcon(selectedCityEntry.count, false)); selectedCityEntry = null; }">✕</button>
    </div>
    <div class="map-city-panel-list">${hotelRows}</div>
  `;

  const viewport = document.querySelector('#screen-map .map-viewport');
  if (viewport) viewport.appendChild(panel);
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
// Title + one line, three counts, one filter row, one sortable table
// (docs/ui-standard.md). The page scrolls; the table header is sticky.

const STRING_COLS = new Set(['name', 'city', 'category', 'brand_group', 'brand', 'status']);

const hotelsState = {
  query: '',
  city:  'all',
  seg:   'all',
  owner: 'all',
  col:   'bar_mad',
  dir:   -1,
};

// Status as plain text: Open, Partly open (under renovation), Closed for the season
const hotelStatus = h => h.under_renovation ? 'Partly open' : h.seasonal_closure ? CLOSED_LABEL : 'Open';
const hotelStatusTip = h => h.under_renovation ? 'Partly open, under renovation: no occupancy estimate; its rooms are left out of the totals.'
  : h.seasonal_closure ? `${CLOSED_NOTE}: no occupancy estimate over the coming 30 nights; its rooms are left out of the totals.` : '';

function filterHotels() {
  const q = fold(hotelsState.query.trim());
  return (hotels || []).filter(h => {
    if (hotelsState.city  !== 'all' && h.city     !== hotelsState.city)  return false;
    if (hotelsState.seg   !== 'all' && h.category !== hotelsState.seg)   return false;
    if (hotelsState.owner !== 'all' && h.owner    !== hotelsState.owner) return false;
    if (q) {
      const haystack = fold([h.name, h.city, dn(h.city), h.brand, h.brand_group, h.owner].join(' '));
      if (!haystack.includes(q)) return false;
    }
    return true;
  });
}

function sortHotels(list) {
  const { col, dir } = hotelsState;
  const val = h => col === 'status' ? hotelStatus(h) : col === 'city' ? dn(h.city || '') : h[col];
  return [...list].sort((a, b) => {
    const va = val(a), vb = val(b);
    if (STRING_COLS.has(col)) return dir * String(va ?? '').localeCompare(String(vb ?? '')) || a.name.localeCompare(b.name);
    if (va == null || vb == null) return (va == null) - (vb == null);   // no figure: always last
    return dir * (va - vb);
  });
}

function syncHotelsSortIcons() {
  document.querySelectorAll('#hotels-table th[data-col]').forEach(th => {
    if (th.dataset.col === hotelsState.col) th.setAttribute('aria-sort', hotelsState.dir === 1 ? 'ascending' : 'descending');
    else th.removeAttribute('aria-sort');
  });
  const sel = document.getElementById('hotels-sort-select');
  if (sel && sel.querySelector(`option[value="${hotelsState.col}"]`)) sel.value = hotelsState.col;
}

function clearAllHotelsFilters() {
  hotelsState.query = '';
  hotelsState.city  = 'all';
  hotelsState.seg   = 'all';
  hotelsState.owner = 'all';
  document.getElementById('hotels-search').value = '';
  document.getElementById('hotels-city-select').value = 'all';
  document.getElementById('hotels-owner-select').value = 'all';
  syncHotelsSeg();
  renderHotelsTable();
}
function syncHotelsSeg() {
  document.querySelectorAll('#hotels-seg [data-hseg]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.hseg === hotelsState.seg)));
}

// Brand group: logo tile + name, linked to its page on Brands
function brandGroupLink(bg, size, from) {
  if (!bg) return '<span class="cell-na">—</span>';
  const tile = getBrandLogoImg(bg, size);
  if (!pipeHasBrandPage(bg)) return `<span class="k-brand">${tile}<span>${fmt.esc(bg)}</span></span>`;
  return `<button type="button" class="k-brand k-brand-link" data-brand-group="${escAttr(bg)}" data-from="${from}"`
    + ` aria-label="${escAttr(bg)}: open on Brands">${tile}<span>${fmt.esc(bg)}</span></button>`;
}

function renderHotelsTable() {
  if (!hotels) return;
  const filtered = filterHotels();
  const sorted   = sortHotels(filtered);
  const total    = hotels.length;

  const today = KodoPeriod.label(KodoPeriod.today());              // "As of 26 Nov 2026"
  const set = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
  set('hkpi-total', total.toLocaleString('en'));
  set('hkpi-cities', new Set(hotels.map(h => h.city)).size);
  set('hkpi-keys', hotels.reduce((s, h) => s + (h.keys || 0), 0).toLocaleString('en'));
  ['hkpi-total-line', 'hkpi-cities-line', 'hkpi-keys-line'].forEach(id => set(id, today));

  set('hotels-results-count', `Showing ${sorted.length} of ${total} hotel${total !== 1 ? 's' : ''}`);

  const tbody = document.getElementById('hotels-tbody');
  if (!sorted.length) {
    tbody.innerHTML = `<tr><td colspan="8" class="k-empty">No hotel matches these filters. <button type="button" class="k-link" onclick="clearAllHotelsFilters()">Clear the filters</button></td></tr>`;
  } else {
    const maxBar = Math.max(0, ...hotels.map(h => h.bar_mad).filter(v => v != null));
    const maxOcc = Math.max(0, ...hotels.map(h => h.occupancy).filter(v => v != null));
    tbody.innerHTML = sorted.map(h => {
      const out = h.under_renovation || h.seasonal_closure;
      const bar = h.bar_mad == null ? KodoBar.hotelCell(h) : `<span class="cell-num">${KodoBar.hotelCell(h)}</span>${inlineBar(h.bar_mad, maxBar, false)}`;
      const occ = out || h.occupancy == null
        ? `<span class="cell-na" title="${escAttr(out ? hotelStatusTip(h) : 'No estimate yet')}">—</span>`
        : `<span class="hotels-occ"><span class="cell-num" title="${EST_TIP}">${fmt.pct(h.occupancy)}</span>${destBadge(h.city)}</span>${inlineBar(h.occupancy, maxOcc, !isOfficial(h.city))}`;
      const tip = hotelStatusTip(h);
      return `<tr data-hid="${h.id}" tabindex="0">
        <td class="hotels-name"><span class="hotels-name-t">${fmt.esc(h.name)}</span><span class="hotels-name-m">${fmt.esc(dn(h.city))}${h.category ? ' · ' + fmt.esc(h.category) : ''}</span></td>
        <td class="col-hide-mobile">${fmt.esc(dn(h.city))}</td>
        <td class="col-hide-mobile">${fmt.esc(h.category || '—')}</td>
        <td class="col-hide-mobile">${brandGroupLink(h.brand_group, 16, 'hotels')}</td>
        <td class="num col-hide-mobile"${out ? ` title="Listed rooms; left out of the totals while ${h.under_renovation ? 'under renovation' : 'closed for the season'}"` : ''}>${fmt.num(out ? h.keys_listed : h.keys)}</td>
        <td class="num cell-metric">${bar}</td>
        <td class="num cell-metric">${occ}</td>
        <td class="col-hide-mobile"><span class="hotels-status"${tip ? ` title="${escAttr(tip)}"` : ''}>${hotelStatus(h)}</span></td>
      </tr>`;
    }).join('');
  }

  syncHotelsSortIcons();
}

// ─── Full render ──────────────────────────────────────────────────

function render() {
  applyDashScope();
  renderKPIs();
  renderBrandTable();
  renderDestTable();
  renderDestHotels();
  renderDashHead();
  // the confidence badges and per-hotel details arrive with the live figures
  KodoLive.load().then(() => { renderBrandTable(); renderDestTable(); renderDestHotels(); renderDashHead(); buildCityFilter(); });
  renderSeason();
  if (googleMap) {
    updateMapMarkers();
    panMap();
  }
}

// ─── Redraw all charts on theme change ────────────────────────────

function redrawChartsForTheme() {
  // Dashboard bar charts
  if (seasonChart) { seasonChart.destroy(); seasonChart = null; renderSeason(); }

  // Pipeline charts
  pipeRestyleMarkers();                              // pipeline markers follow the theme

  // Tourism charts — destroy and reset flag; reinit if screen is active
  if (tourismInited) {
    TOUR_CHART_IDS.forEach(id => { const c = Chart.getChart(id); if (c) c.destroy(); });
    tourismInited = false;
    const tourismEl = document.getElementById('screen-tourism');
    if (tourismEl && tourismEl.classList.contains('active')) {
      initTourismCharts();
    }
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
// Official figures and the Kodo figures both come from /api/tourism
// (tourism.json and tourism_forecast.json; the source records stay on the
// server). Three states, always labelled: 2025 and earlier are official,
// 2026E is a Kodo estimate (official months so far plus the model for the
// rest of the year), 2027F is a Kodo forecast with its range.

let tourismData = null;
let tourismLoading = null;

const TOUR_YEARS = [2019, 2023, 2024, 2025];
const TOUR_CHART_IDS = ['chart-tour-arrivals', 'chart-tour-transport', 'chart-tour-origins', 'chart-tour-tesmre',
  'chart-tour-nights', 'chart-tour-occ', 'chart-tour-airports', 'chart-tour-revenue', 'chart-tour-season'];
const TOUR_MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

const tourSeries = id => tourismData.series.find(s => s.id === id);
const tourAnnual = id => {
  const s = tourSeries(id), out = {};
  if (s) s.points.forEach(p => { if (/^\d{4}$/.test(p.period)) out[+p.period] = p.value; });
  return out;
};
const tourBy = metric => tourismData.series.filter(s => s.metric === metric);
const tourM = v => v == null ? '—' : (v / 1e6).toFixed(1) + 'M';
const tourB = v => v == null ? '—' : (v / 1000).toFixed(1) + 'B';     // MAD million → billions
const tourPct = (a, b) => (a == null || b == null || !b) ? null : (a / b - 1) * 100;
const tourSigned = (v, d = 1) => (v >= 0 ? '+' : '−') + Math.abs(v).toFixed(d);
// Change from 2026E to 2027F, from the published base values (cards and tables use the same)
const tourChange = (a, b, pts) => (a == null || b == null) ? '—'
  : pts ? `${tourSigned(b - a)} pts` : `${tourSigned(tourPct(b, a))}%`;
// "Jan–Oct 2026" from a year-to-date period '2026-01/2026-10'
const tourSpan = p => { const [a, b] = p.split('/'); return `${TOUR_MON[+a.slice(5) - 1]}–${TOUR_MON[+b.slice(5) - 1]} ${b.slice(0, 4)}`; };
const TOUR_TAG = { est: '<span class="tour-tag tour-tag--est">est.</span>', fc: '<span class="tour-tag tour-tag--fc">fcst.</span>' };

// Year selector: the official years, then Kodo's 2026E estimate and 2027F
// forecast. A year key is '2025' (official) or '2026E' / '2027F'; every
// figure for a Kodo year comes from tourism_forecast.json, the same figures
// as the Outlook section, so the two never disagree. What is not forecast
// says "Not forecast", never a blank, a zero or the 2025 value.
const TOUR_KODO = { '2026E': { year: 2026, kind: 'est', prev: '2025', note: 'Kodo estimate, not official' },
                    '2027F': { year: 2027, kind: 'fc', prev: '2026E', note: 'Kodo forecast, not official' } };
const TOUR_NOT = 'Not forecast';
const tourKey = v => { const s = String(v || '2025').toUpperCase(); return TOUR_KODO[s] ? s : String(parseInt(s, 10) || 2025); };
const tourIsKodo = key => !!TOUR_KODO[key];

// Every figure of one year: {kind, label, arrivals, nights, receipts, occ, air: {base, low?, high?} | null,
// markets, regions, cities, airports: {name: value}, notMarkets, notCities}
function tourYearFigures(key) {
  key = tourKey(key);
  const F = tourismData.forecast, NF = F.not_forecast || {};
  if (key === '2026E') {
    const N = F.nowcast_2026, E = F.estimate_2026 || {};
    return { kind: 'est', label: '2026E', arrivals: N.arrivals, nights: N.nights, receipts: N.receipts, occ: N.occupancy,
             air: N.air_passengers, markets: E.markets || {}, regions: E.regions || {}, cities: E.cities_occupancy || {},
             airports: E.airports || {}, notMarkets: NF.markets || [], notCities: NF.cities || [] };
  }
  if (key === '2027F') {
    const P = F.forecast_2027, base = o => Object.fromEntries(Object.entries(o || {}).map(([k, v]) => [k, v.base]));
    return { kind: 'fc', label: '2027F', arrivals: P.arrivals, nights: P.nights, receipts: P.receipts, occ: P.occupancy,
             air: P.air_passengers, markets: base(F.markets_2027), regions: base(F.regions_2027), cities: base(F.cities_occupancy_2027),
             airports: base(F.airports_2027), ranges: { markets: F.markets_2027, regions: F.regions_2027, cities: F.cities_occupancy_2027, airports: F.airports_2027 },
             notMarkets: NF.markets || [], notCities: NF.cities || [] };
  }
  const y = +key, one = id => { const v = tourAnnual(id)[y]; return v == null ? null : { base: v }; };
  const pick = (metric, dimKey, prefix) => Object.fromEntries(tourBy(metric).map(s => [s.dim[dimKey], s.points.find(p => p.period === String(y))?.value])
    .filter(([k, v]) => v != null && k !== 'Other' && k !== 'Morocco'));
  return { kind: 'official', label: String(y), arrivals: one('arrivals_total'), nights: one('nights_total'), receipts: one('receipts_total'),
           occ: one('occupancy_Morocco'), air: one('air_passengers_total'), markets: pick('arrivals_by_market', 'key'),
           regions: pick('nights_by_region', 'key'), cities: pick('occupancy', 'city'),
           airports: Object.fromEntries(tourBy('airport_passengers').filter(s => s.freq === 'A').map(s => [s.dim.airport, tourAnnual(s.id)[y]]).filter(x => x[1] != null)),
           notMarkets: [], notCities: [] };
}

function tourismKpiPeriods(key) {
  const ids = ['tour-kpi-arrivals', 'tour-kpi-nights', 'tour-kpi-revenue', 'tour-kpi-occ', 'tour-kpi-origin'];
  if (tourIsKodo(key)) ids.forEach(id => KodoPeriod.setText(id, `${key} · ${TOUR_KODO[key].note}`));
  else ids.forEach(id => KodoPeriod.set(id, { kind: 'year', year: +key }, null));
}

function setTourismYear(v) {
  if (!tourismData) return;
  const key = tourKey(v), kodo = TOUR_KODO[key];
  const sel = document.getElementById('tourism-export-year');
  if (sel && sel.value !== key) sel.value = key;
  tourismKpiPeriods(key);
  const cur = tourYearFigures(key);
  const prevKey = kodo ? kodo.prev : String(+key - 1);
  const prev = tourYearFigures(prevKey);

  const card = (k, value, delta, deltaText, status, range) => {
    const el = document.getElementById(`tour-kpi-${k}`);
    const v = document.getElementById(`tour-kpi-${k}-value`);
    if (v) {
      v.textContent = value;
      v.title = status ? 'Provisional figure, may be revised' : '';
      v.classList.toggle('tour-kpi-value--kodo', !!kodo);
      v.classList.toggle('tour-kpi-value--na', value === TOUR_NOT);
    }
    // the "est." / "fcst." tag after the card's label, as in the Outlook section
    const lab = el && el.querySelector('.kpi-label');
    if (lab) {
      let tag = lab.querySelector('.tour-tag');
      if (kodo) {
        if (!tag) { lab.insertAdjacentHTML('beforeend', ' <span class="tour-tag"></span>'); tag = lab.querySelector('.tour-tag'); }
        tag.className = `tour-tag tour-tag--${kodo.kind}`;
        tag.textContent = kodo.kind === 'est' ? 'est.' : 'fcst.';
      } else if (tag) tag.remove();
    }
    if (el) {
      let r = el.querySelector('.tour-kpi-range');
      if (range) { if (!r) { r = document.createElement('span'); r.className = 'tour-kpi-range'; el.querySelector('.kpi-meta').after(r); } r.textContent = range; }
      else if (r) r.remove();
    }
    const d = document.getElementById(`tour-kpi-${k}-delta`);
    if (!d) return;
    if (delta == null) { d.style.display = 'none'; return; }
    d.textContent = deltaText;
    d.className = 'kpi-delta ' + (delta < 0 ? 'down pill--red' : 'up pill--green');
    d.style.display = '';
  };
  const vs = kodo ? `vs ${prevKey}` : KodoPeriod.vs({ kind: 'year', year: +key - 1 });
  // changes from the published base values, as the Outlook cards and tables compute them
  const pctCard = (k, f, p, fmt, status) => {
    if (!f) { card(k, kodo ? TOUR_NOT : '—', null); return; }
    const d = p ? tourPct(f.base, p.base) : null;
    const text = d == null ? null : (kodo ? `${tourChange(p.base, f.base)} vs ${prevKey}` : `${tourSigned(d, 0)}% ${vs}`);
    card(k, fmt(f.base), d, text, status, f.low != null && kodo && kodo.kind === 'fc' ? `range ${fmt(f.low)} – ${fmt(f.high)}` : null);
  };
  pctCard('arrivals', cur.arrivals, prev.arrivals, tourM);
  pctCard('nights', cur.nights, prev.nights, tourM);
  const recStatus = kodo ? null : tourSeries('receipts_total').points.find(p => p.period === key)?.status;
  pctCard('revenue', cur.receipts, prev.receipts, v => 'MAD ' + tourB(v), recStatus === 'provisional');
  {
    const f = cur.occ, p = prev.occ, fmt = v => kodo ? (+v).toFixed(1) + '%' : v + '%';
    if (!f || f.base == null) card('occ', kodo ? TOUR_NOT : '—', null);
    else {
      const d = p && p.base != null ? f.base - p.base : null;
      card('occ', fmt(f.base), d, d == null ? null : (kodo ? `${tourChange(p.base, f.base, true)} vs ${prevKey}` : `${tourSigned(d, 0)} pts ${vs}`),
           false, f.low != null && kodo && kodo.kind === 'fc' ? `range ${fmt(f.low)} – ${fmt(f.high)}` : null);
    }
  }
  const occMeta = document.querySelector('#tour-kpi-occ .kpi-meta');
  if (occMeta) occMeta.textContent = cur.occ ? 'classified accommodation' : 'not published on the current basis';

  // Top market of residence (MRE included)
  const mk = Object.entries(cur.markets).sort((a, b) => b[1] - a[1]);
  if (mk.length && cur.arrivals) {
    card('origin', mk[0][0]);
    document.getElementById('tour-kpi-origin-meta').textContent = `${(mk[0][1] / cur.arrivals.base * 100).toFixed(0)}% of arrivals, MRE included`;
  } else if (kodo) {
    card('origin', TOUR_NOT);
    document.getElementById('tour-kpi-origin-meta').textContent = 'markets not forecast for this year';
  }

  // Breakdown charts for the selected year
  const upd = (id, labels, values) => { const c = Chart.getChart(id); if (c) { c.data.labels = labels; c.data.datasets[0].data = values; c.update(); } };
  const o = kodo ? tourOriginsKodo(cur) : tourOrigins(+key), n = kodo ? tourRegionsKodo(cur) : tourRegions(+key);
  upd('chart-tour-origins', o.labels, o.values);
  upd('chart-tour-nights', n.labels, n.values);
  document.getElementById('tour-origins-unit').textContent = `${cur.label} · % of arrivals` + (kodo ? ' · Kodo, not official' : '');
  document.getElementById('tour-nights-unit').textContent = `${cur.label} · millions · classified accommodation` + (kodo ? ' · Kodo, not official' : '');
  tourPairCharts(key, cur, prevKey, prev);
  tourNotForecastNotes(key);
  tourHighlightYearColumn(key);
}

// Origin markets for a Kodo year: the markets forecast, then the rest
// ("Other markets", with the markets not forecast named)
function tourOriginsKodo(cur) {
  const rows = Object.entries(cur.markets).sort((a, b) => b[1] - a[1]);
  const total = cur.arrivals ? cur.arrivals.base : null;
  if (!total) return { labels: [], values: [] };
  const rest = total - rows.reduce((s, r) => s + r[1], 0);
  rows.push([cur.notMarkets.length ? `Other markets (incl. ${cur.notMarkets.join(', ')}: not forecast)` : 'Other markets', rest]);
  return { labels: rows.map(r => r[0]), values: rows.map(r => +(r[1] / total * 100).toFixed(1)) };
}

function tourRegionsKodo(cur) {
  const rows = Object.entries(cur.regions).sort((a, b) => b[1] - a[1]);
  if (cur.nights) rows.push(['Other regions', cur.nights.base - rows.reduce((s, r) => s + r[1], 0)]);
  return { labels: rows.map(r => r[0]), values: rows.map(r => +(r[1] / 1e6).toFixed(2)) };
}

// Occupancy by city and airport passengers: two years side by side. An
// official year shows 2024 and 2025 (the years published on the current
// basis); 2026E shows 2025 and 2026E; 2027F shows 2026E and 2027F. A city or
// airport not forecast says so in its label.
function tourPairCharts(key, cur, prevKey, prev) {
  const kodo = tourIsKodo(key), cc = getChartColors();
  const pair = kodo ? [[prevKey, prev], [key, cur]] : [['2024', tourYearFigures('2024')], ['2025', tourYearFigures('2025')]];
  const colour = k => tourIsKodo(k) ? withAlpha(cc.forecastColor, k === '2026E' ? 0.45 : 0.85) : (k === pair[1][0] ? cc.barColor : cc.compColor);
  const occChart = Chart.getChart('chart-tour-occ');
  if (occChart) {
    const off = tourYearFigures('2025').cities;
    const cities = Object.keys(off).sort((a, b) => (off[b] || 0) - (off[a] || 0));
    const nf = c => kodo && pair.some(([, f]) => f.kind !== 'official' && f.cities[c] == null);
    occChart.data.labels = cities.map(c => nf(c) ? `${c} (${TOUR_NOT.toLowerCase()})` : c);
    occChart.options.plugins.datalabels.display = ctx => ctx.dataset.data[ctx.dataIndex] != null;
    occChart.data.datasets = pair.map(([k, f]) => ({ label: k, data: cities.map(c => f.cities[c] == null ? null : +(+f.cities[c]).toFixed(kodo ? 1 : 0)),
      backgroundColor: colour(k), borderRadius: 3, borderSkipped: false }));
    occChart.update();
    const m = pair.map(([k, f]) => `${f.occ ? (+f.occ.base).toFixed(kodo ? 1 : 0) : TOUR_NOT}% in ${k}`.replace(`${TOUR_NOT}%`, TOUR_NOT));
    document.getElementById('tour-occ-note').textContent = kodo
      ? `Morocco: ${m.join(', ')}. ${key} is a ${TOUR_KODO[key].note}; cities not forecast are marked.`
      : `Morocco: ${m.join(', ')}. Current official basis; earlier years were published on a different basis and are not comparable.`;
  }
  const apChart = Chart.getChart('chart-tour-airports');
  if (apChart) {
    const names = apChart.$kodoAirports || (apChart.$kodoAirports = [...apChart.data.labels]);
    apChart.data.labels = names.map(a => kodo && pair.some(([, f]) => f.kind !== 'official' && f.airports[a] == null) ? `${a} (${TOUR_NOT.toLowerCase()})` : a);
    apChart.options.plugins.datalabels.display = ctx => ctx.dataset.data[ctx.dataIndex] != null;
    apChart.data.datasets = pair.map(([k, f]) => ({ label: k, data: names.map(a => f.airports[a] == null ? null : +(f.airports[a] / 1e6).toFixed(2)),
      backgroundColor: colour(k), borderRadius: 3, borderSkipped: false }));
    apChart.update();
    const note = document.getElementById('tour-airports-note');
    if (kodo) {
      note.dataset.official = note.dataset.official || note.textContent;
      note.textContent = `All airports: ${pair.map(([k, f]) => `${f.air ? tourM(f.air.base) : TOUR_NOT} in ${k}`).join(', ')}. `
        + `${key} is a ${TOUR_KODO[key].note}. Airport figures are not backtested.`;
    } else if (note.dataset.official) note.textContent = note.dataset.official;
  }
}

// Charts with no Kodo figure for 2026E and 2027F say so
function tourNotForecastNotes(key) {
  const kodo = tourIsKodo(key);
  [['twrap-transport', 'Arrivals by entry mode'], ['twrap-tesmre', 'Foreign tourists vs MRE']].forEach(([wrap, what]) => {
    const card = document.getElementById(wrap)?.closest('.chart-card');
    if (!card) return;
    let el = card.querySelector('.tour-nf-note');
    if (kodo) {
      if (!el) { el = document.createElement('p'); el.className = 'tour-note tour-nf-note'; card.appendChild(el); }
      el.textContent = `${what}: ${TOUR_NOT.toLowerCase()} for ${key}. The chart shows official years only.`;
    } else if (el) el.remove();
  });
}

// The selected year's column in the Outlook tables
function tourHighlightYearColumn(key) {
  const y = tourIsKodo(key) ? String(TOUR_KODO[key].year) : null;     // official years: no highlight
  document.querySelectorAll('#tour-fc .tour-table [data-year]').forEach(el => el.classList.toggle('tour-col-sel', el.dataset.year === y));
}

function tourOrigins(yr) {
  const arr = tourAnnual('arrivals_total')[yr];
  const rows = tourBy('arrivals_by_market').filter(s => s.dim.key !== 'Other')
    .map(s => [s.dim.key, s.points.find(p => p.period === String(yr))?.value || 0]).sort((a, b) => b[1] - a[1]).slice(0, 10);
  const top = rows.reduce((a, r) => a + r[1], 0);
  rows.push(['Other markets', arr - top]);
  return { labels: rows.map(r => r[0]), values: rows.map(r => +(r[1] / arr * 100).toFixed(1)) };
}

function tourRegions(yr) {
  const rows = tourBy('nights_by_region').map(s => [s.dim.key, s.points.find(p => p.period === String(yr))?.value || 0])
    .sort((a, b) => b[1] - a[1]);
  return { labels: rows.map(r => r[0]), values: rows.map(r => +(r[1] / 1e6).toFixed(2)) };
}

async function loadTourismData() {
  if (tourismData) return tourismData;
  if (!tourismLoading) {
    tourismLoading = fetch('/api/tourism', { credentials: 'same-origin' })
      .then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then(d => (tourismData = d))
      .finally(() => { tourismLoading = null; });
  }
  return tourismLoading;
}

function initTourismCharts() {
  if (tourismInited) return;
  if (!tourismData) {
    loadTourismData().then(() => initTourismCharts()).catch(e => {
      console.error('Tourism data failed to load:', e);
      const y = document.getElementById('tour-ytd');
      if (y) y.textContent = 'Tourism figures could not be loaded. Refresh the page to try again.';
    });
    return;
  }
  TOUR_CHART_IDS.forEach(id => { const c = Chart.getChart(id); if (c) c.destroy(); });
  const cc = getChartColors();
  const F = tourismData.forecast, F27 = F.forecast_2027, N26 = F.nowcast_2026;
  const setH = (id, h) => { const el = document.getElementById(id); el.style.minHeight = '0'; el.style.height = h + 'px'; };
  const tip = () => ({
    backgroundColor: cc.tooltipBg, borderColor: cc.tooltipBdr, borderWidth: 1,
    titleColor: cc.tooltipTtl, bodyColor: cc.tooltipBdy, padding: { top: 8, bottom: 8, left: 12, right: 12 },
  });
  const ticks = { color: cc.tick, font: { size: 11, weight: '400', family: "'Sweet Sans Pro', sans-serif" } };
  const fcFill = withAlpha(cc.forecastColor, 0.28), estFill = withAlpha(cc.forecastColor, 0.12);
  const covidColor = cc.compColor;

  // Official bars, then the 2026E estimate and the 2027F forecast with a floating range bar
  function trendChart(canvasId, hist, est, fc, scale, unitFmt, firstYear) {
    const years = Object.keys(hist).map(Number).filter(y => y >= firstYear).sort();
    const labels = years.map(String).concat(['2026E', '2027F']);
    const n = years.length;
    const off = years.map(y => +(hist[y] / scale).toFixed(2)).concat([null, null]);
    const kodo = Array(n).fill(null).concat([+(est.base / scale).toFixed(2), +(fc.base / scale).toFixed(2)]);
    const range = Array(n).fill(null).concat([[est.low / scale, est.high / scale], [fc.low / scale, fc.high / scale]]);
    return new Chart(document.getElementById(canvasId), {
      type: 'bar',
      data: {
        labels,
        datasets: [
          { label: 'Official', data: off, order: 2, borderRadius: 4, borderSkipped: false,
            backgroundColor: years.map(y => (y === 2020 || y === 2021) ? covidColor : cc.barColor).concat([null, null]) },
          { label: 'Kodo', data: kodo, order: 2, borderRadius: 4, borderSkipped: false,
            backgroundColor: Array(n).fill(null).concat([estFill, fcFill]),
            borderColor: cc.forecastColor, borderWidth: Array(n).fill(0).concat([1, 1.5]) },
          { label: 'Range', data: range, order: 1, backgroundColor: cc.forecastColor, barPercentage: 0.12, categoryPercentage: 1,
            datalabels: { display: false } },
        ],
      },
      options: {
        responsive: true, maintainAspectRatio: false, animation: { duration: 350 },
        layout: { padding: { top: 28 } },
        datasets: { bar: { grouped: false } },
        plugins: {
          legend: { display: false },
          tooltip: {
            ...tip(),
            filter: item => item.raw != null && item.dataset.label !== 'Range',
            callbacks: {
              label: ctx => {
                const i = ctx.dataIndex;
                if (ctx.dataset.label === 'Official') {
                  const y = years[i];
                  return '  Official: ' + unitFmt(ctx.raw) + ((y === 2020 || y === 2021) ? ' (COVID year)' : '');
                }
                const r = range[i];
                return `  ${i === n ? '2026E estimate' : '2027F forecast'}: ${unitFmt(ctx.raw)} (range ${unitFmt(r[0])}–${unitFmt(r[1])})`;
              },
            },
          },
          datalabels: {
            anchor: 'end', align: 'top', clip: false, color: cc.label, font: { size: 10, weight: '600' },
            display: ctx => ctx.dataset.label !== 'Range' && ctx.raw != null,
            formatter: v => (+v).toFixed(1),
          },
        },
        scales: { x: { ticks: { ...ticks, padding: 6 } }, y: { beginAtZero: true, ticks } },
      },
    });
  }

  // 1. Arrivals trend
  setH('twrap-arrivals', 300);
  trendChart('chart-tour-arrivals', tourAnnual('arrivals_total'), N26.arrivals, F27.arrivals, 1e6, v => (+v).toFixed(1) + 'M', 2013);

  // 2. Entry mode (official: 2019, 2023-2025)
  setH('twrap-transport', 290);
  {
    const modes = ['Air', 'Sea', 'Land'].map(m => tourAnnual('arrivals_mode_' + m));
    new Chart(document.getElementById('chart-tour-transport'), {
      type: 'bar',
      data: {
        labels: TOUR_YEARS.map(String),
        datasets: ['Air', 'Sea', 'Land'].map((m, i) => ({
          label: m, data: TOUR_YEARS.map(y => +(modes[i][y] / 1e6).toFixed(2)),
          backgroundColor: [cc.barColor, cc.barColor2, cc.barColor3][i], borderRadius: 3, borderSkipped: false,
        })),
      },
      options: {
        responsive: true, maintainAspectRatio: false, animation: { duration: 350 }, layout: { padding: { top: 12 } },
        plugins: {
          legend: { display: true, position: 'bottom', labels: { color: cc.label, boxWidth: 10, font: { size: 11 } } },
          datalabels: { display: false },
          tooltip: { ...tip(), callbacks: { label: ctx => `  ${ctx.dataset.label}: ${(+ctx.raw).toFixed(2)}M` } },
        },
        scales: { x: { ticks: { ...ticks, padding: 8 } }, y: { beginAtZero: true, ticks } },
      },
    });
  }

  // 3. Origin markets (selected year)
  const yr0 = +(tourIsKodo(tourKey(document.getElementById('tourism-export-year')?.value)) ? 2025 : tourKey(document.getElementById('tourism-export-year')?.value));
  const key0 = tourKey(document.getElementById('tourism-export-year')?.value);
  {
    const o = tourOrigins(yr0);
    setH('twrap-origins', Math.max(260, o.labels.length * 30 + 50));
    const cfg = chartConfig(o.labels, o.values, '%', o.labels.map(() => cc.barColor), v => v + '%');
    cfg.options.plugins.tooltip.callbacks.label = ctx => '  ' + ctx.raw + '% of arrivals';
    new Chart(document.getElementById('chart-tour-origins'), lightenCityChartLabels(cfg));
  }

  // 4. Foreign tourists and MRE (2019-2024; no split from 2025)
  setH('twrap-tesmre', 290);
  {
    const tes = tourAnnual('arrivals_tes'), mre = tourAnnual('arrivals_mre');
    const ys = Object.keys(tes).map(Number).sort();
    new Chart(document.getElementById('chart-tour-tesmre'), {
      type: 'bar',
      data: {
        labels: ys.map(y => (y === 2020 || y === 2021) ? `${y} (COVID)` : String(y)),
        datasets: [
          { label: 'Foreign tourists', data: ys.map(y => +(tes[y] / 1e6).toFixed(2)), backgroundColor: cc.barColor, stack: 's' },
          { label: 'MRE', data: ys.map(y => +(mre[y] / 1e6).toFixed(2)), backgroundColor: cc.barColor2, stack: 's' },
        ],
      },
      options: {
        responsive: true, maintainAspectRatio: false, animation: { duration: 350 },
        plugins: {
          legend: { display: true, position: 'bottom', labels: { color: cc.label, boxWidth: 10, font: { size: 11 } } },
          datalabels: { display: false },
          tooltip: { ...tip(), callbacks: { label: ctx => `  ${ctx.dataset.label}: ${(+ctx.raw).toFixed(2)}M` } },
        },
        scales: { x: { stacked: true, ticks }, y: { stacked: true, beginAtZero: true, ticks } },
      },
    });
  }

  // 5. Nights by region (selected year)
  {
    const r = tourRegions(yr0);
    setH('twrap-nights', Math.max(260, r.labels.length * 28 + 50));
    const cfg = chartConfig(r.labels, r.values, 'M', r.labels.map(() => cc.barColor), v => (+v).toFixed(1) + 'M');
    cfg.options.plugins.tooltip.callbacks.label = ctx => '  ' + (+ctx.raw).toFixed(2) + 'M nights';
    new Chart(document.getElementById('chart-tour-nights'), lightenCityChartLabels(cfg));
  }

  // 6. Occupancy by city, 2024 vs 2025
  {
    const rows = tourBy('occupancy').filter(s => s.dim.city !== 'Morocco')
      .map(s => [s.dim.city, tourAnnual(s.id)]).sort((a, b) => b[1][2025] - a[1][2025]);
    setH('twrap-occ', Math.max(280, rows.length * 34 + 60));
    new Chart(document.getElementById('chart-tour-occ'), {
      type: 'bar',
      data: {
        labels: rows.map(r => r[0]),
        datasets: [
          { label: '2024', data: rows.map(r => r[1][2024]), backgroundColor: cc.compColor, borderRadius: 3, borderSkipped: false },
          { label: '2025', data: rows.map(r => r[1][2025]), backgroundColor: cc.barColor, borderRadius: 3, borderSkipped: false },
        ],
      },
      options: {
        indexAxis: 'y', responsive: true, maintainAspectRatio: false, animation: { duration: 350 },
        layout: { padding: { right: 36 } },
        plugins: {
          legend: { display: true, position: 'bottom', labels: { color: cc.label, boxWidth: 10, font: { size: 11 } } },
          datalabels: { anchor: 'end', align: 'right', clip: false, color: cc.label, font: { size: 10, weight: '500' }, formatter: v => v + '%' },
          tooltip: { ...tip(), callbacks: { label: ctx => `  ${ctx.dataset.label}: ${ctx.raw}%` } },
        },
        scales: { x: { min: 0, max: 100, ticks }, y: { ticks: { color: cc.catLabel, font: { size: 11 } } } },
      },
    });
    const m = tourAnnual('occupancy_Morocco');
    document.getElementById('tour-occ-note').textContent =
      `Morocco: ${m[2024]}% in 2024, ${m[2025]}% in 2025. Current official basis; earlier years were published on a different basis and are not comparable.`;
  }

  // 7. Airport passengers, 2024 vs 2025 (a secondary source)
  {
    const aps = tourBy('airport_passengers').filter(s => s.freq === 'A');
    setH('twrap-airports', Math.max(240, aps.length * 44 + 60));
    new Chart(document.getElementById('chart-tour-airports'), {
      type: 'bar',
      data: {
        labels: aps.map(s => s.dim.airport),
        datasets: [2024, 2025].map((y, i) => ({
          label: String(y), data: aps.map(s => +(tourAnnual(s.id)[y] / 1e6).toFixed(2)),
          backgroundColor: i ? cc.barColor : cc.compColor, borderRadius: 3, borderSkipped: false,
        })),
      },
      options: {
        indexAxis: 'y', responsive: true, maintainAspectRatio: false, animation: { duration: 350 },
        layout: { padding: { right: 40 } },
        plugins: {
          legend: { display: true, position: 'bottom', labels: { color: cc.label, boxWidth: 10, font: { size: 11 } } },
          datalabels: { anchor: 'end', align: 'right', clip: false, color: cc.label, font: { size: 10, weight: '500' }, formatter: v => (+v).toFixed(1) + 'M' },
          tooltip: { ...tip(), callbacks: { label: ctx => `  ${ctx.dataset.label}: ${(+ctx.raw).toFixed(2)}M passengers` + (ctx.label.startsWith('Casablanca') && ctx.dataset.label === '2025' ? ' (rounded)' : '') } },
        },
        scales: { x: { beginAtZero: true, ticks }, y: { ticks: { color: cc.catLabel, font: { size: 11 } } } },
      },
    });
    const tot = tourAnnual('air_passengers_total');
    const ytd = tourSeries('air_passengers_ytd').points[0];
    const ytdAp = tourBy('airport_passengers').filter(s => s.freq === 'YTD')
      .map(s => `${s.dim.airport.split(' ')[0]} ${tourM(s.points[0].value)}`).join(', ');
    document.getElementById('tour-airports-note').textContent =
      `All airports: ${tourM(tot[2024])} in 2024, ${tourM(tot[2025])} in 2025; ${tourM(ytd.value)} in Jan–Aug 2026 (${tourSigned(ytd.yoy_pct)}%). `
      + `Jan–Aug 2026: ${ytdAp}. Casablanca 2025 is rounded. Fès and Tanger annual totals are not shown: the published figures could not be confirmed.`;
  }

  // 8. Receipts trend
  setH('twrap-revenue', 290);
  trendChart('chart-tour-revenue', tourAnnual('receipts_total'), N26.receipts, F27.receipts, 1000, v => 'MAD ' + (+v).toFixed(1) + 'B', 2013);

  // 9. Receipts by month: 2025, 2026 official, 2026E for the remaining months, 2027F with its range
  setH('twrap-season', 290);
  {
    const mon = {};
    tourSeries('receipts_monthly').points.forEach(p => { mon[p.period] = p.value / 1000; });
    const yr = y => TOUR_MON.map((_, i) => mon[`${y}-${String(i + 1).padStart(2, '0')}`] ?? null);
    const fm = F27.receipts.monthly;
    const last26 = Object.keys(mon).filter(k => k.startsWith('2026')).sort().pop();
    // 2026E continues the official line from its last month
    const est26 = TOUR_MON.map(() => null);
    const lastIdx = +last26.slice(5) - 1;
    est26[lastIdx] = mon[last26];
    (F.estimate_2026?.receipts_monthly || []).forEach(m => { est26[+m.month.slice(5) - 1] = m.value / 1000; });
    const estFrom = (F.estimate_2026?.receipts_monthly || [])[0]?.month;
    new Chart(document.getElementById('chart-tour-season'), {
      type: 'line',
      data: {
        labels: TOUR_MON,
        datasets: [
          { label: '2027F low', data: fm.map(m => m.low / 1000), borderWidth: 0, pointRadius: 0, fill: false },
          { label: '2027F range', data: fm.map(m => m.high / 1000), borderWidth: 0, pointRadius: 0, backgroundColor: withAlpha(cc.forecastColor, 0.16), fill: '-1' },
          { label: '2027F forecast', data: fm.map(m => m.base / 1000), borderColor: cc.forecastColor, borderDash: [5, 4], borderWidth: 2, pointRadius: 2, tension: 0.3, fill: false },
          { label: '2025 official', data: yr(2025), borderColor: cc.compColor, borderWidth: 2, pointRadius: 2, tension: 0.3, fill: false },
          { label: '2026 official', data: yr(2026), borderColor: cc.barColor, borderWidth: 2, pointRadius: 2, tension: 0.3, fill: false },
          { label: '2026E estimate', data: est26, borderColor: cc.barColor, borderDash: [2, 3], borderWidth: 2, pointRadius: 2,
            pointStyle: 'circle', pointBackgroundColor: 'transparent', tension: 0.3, fill: false },
        ],
      },
      options: {
        responsive: true, maintainAspectRatio: false, animation: { duration: 350 },
        plugins: {
          legend: { display: false }, datalabels: { display: false },
          tooltip: {
            ...tip(), mode: 'index', intersect: false,
            filter: item => !['2027F low', '2027F range'].includes(item.dataset.label) && item.raw != null
              && !(item.dataset.label === '2026E estimate' && item.dataIndex === lastIdx),
            callbacks: {
              label: ctx => {
                if (ctx.dataset.label.startsWith('2027F')) {
                  const m = fm[ctx.dataIndex];
                  return `  2027F forecast: MAD ${(m.base / 1000).toFixed(1)}B (range ${(m.low / 1000).toFixed(1)}–${(m.high / 1000).toFixed(1)})`;
                }
                return `  ${ctx.dataset.label}: MAD ${(+ctx.raw).toFixed(1)}B`;
              },
            },
          },
        },
        scales: { x: { ticks }, y: { beginAtZero: true, ticks } },
      },
    });
    const [ly, lm] = last26.split('-').map(Number);
    document.getElementById('tour-season-legend').innerHTML = [
      ['tour-dot-official', `2026 official (to ${TOUR_MON[lm - 1]} ${ly})`],
      ...(estFrom ? [['tour-dot-estimate', `2026E estimate (${TOUR_MON[+estFrom.slice(5) - 1]}–Dec)`]] : []),
      ['tour-dot-prior', '2025 official'],
      ['tour-dot-forecast', '2027F forecast, with range'],
    ].map(([c, t]) => `<span class="chart-dot-legend-item"><span class="chart-dot-legend-dot ${c}"></span>${t}</span>`).join('');
  }

  renderTourismPanels();
  const yearSel = document.getElementById('tourism-export-year');
  if (yearSel) yearSel.onchange = e => setTourismYear(e.target.value);
  setTourismYear(key0);
  EventCalendar.init();
  tourismInited = true;
}

// The 2026 year-to-date strip, the outlook section (2026E and 2027F), the
// catalysts and the notes on reading the figures
function renderTourismPanels() {
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const last = id => tourSeries(id).points[tourSeries(id).points.length - 1];

  // 2026 so far
  const ytd = [
    ['Arrivals', last('arrivals_ytd'), v => tourM(v)],
    ['Tourist nights', last('nights_ytd'), v => tourM(v)],
    ['Travel receipts', last('receipts_ytd'), v => 'MAD ' + tourB(v)],
    ['Airport passengers', last('air_passengers_ytd'), v => tourM(v)],
  ];
  document.getElementById('tour-ytd').innerHTML =
    `<span class="tour-ytd-title">2026 so far <span class="pill--grey tour-ytd-pill">provisional</span></span>` +
    ytd.map(([l, p, f]) => `<span class="tour-ytd-item">
        <span class="tour-ytd-label">${l} · ${tourSpan(p.period)}</span>
        <span class="tour-ytd-value">${f(p.value)}</span>
        <span class="tour-ytd-delta">${tourSigned(p.yoy_pct)}% vs same period 2025</span></span>`).join('');

  // Outlook: 2026E estimate and 2027F forecast
  const F = tourismData.forecast, F27 = F.forecast_2027, N26 = F.nowcast_2026, BT = F.backtest, E26 = F.estimate_2026 || {};
  document.getElementById('tour-fc-intro').innerHTML =
    'Kodo’s own figures, built from the official figures above; they are not official. '
    + '<strong>2026E</strong> is an estimate: the official months published so far plus Kodo’s model for the rest of the year. '
    + '<strong>2027F</strong> is a forecast: a base case with a low–high range, wider where the history is short. '
    + '<a href="/methodology#tourism-forecast">Method, assumptions and backtest</a>.';
  const pct = v => v.toFixed(1) + '%';
  const cards = [
    ['Arrivals', F27.arrivals, tourM, N26.arrivals, BT.arrivals],
    ['Tourist nights', F27.nights, tourM, N26.nights, BT.nights],
    ['Occupancy', F27.occupancy, pct, N26.occupancy, BT.occupancy, true],
    ['Travel receipts', F27.receipts, v => 'MAD ' + tourB(v), N26.receipts, BT.receipts],
    ['Airport passengers', F27.air_passengers, tourM, N26.air_passengers, BT.air_passengers],
  ].filter(c => c[1]);
  document.getElementById('tour-fc-grid').innerHTML = cards.map(([l, f, fmt, n, bt, pts]) => `
    <div class="tour-fc-card">
      <span class="tour-fc-label">${l} · 2027F</span>
      <span class="tour-fc-value">${fmt(f.base)}</span>
      <span class="tour-fc-range">range ${fmt(f.low)} – ${fmt(f.high)}</span>
      ${n && n.base != null ? `<span class="tour-fc-meta"><span class="tour-fc-est">2026E estimate ${fmt(n.base)}</span> · ${tourChange(n.base, f.base, pts)} to 2027F</span>` : ''}
      <span class="tour-fc-meta">Backtest error ${bt.mape_v2}%${Object.keys(bt.years).length > 1 ? ' (average)' : ' (one year)'}</span>
    </div>`).join('');

  // Tables: 2025 (official) | 2026E | 2027F | range of 2027F | change 2026E → 2027F; the total row matches the cards
  const head = first => `<thead><tr><th>${first}</th><th data-year="2025">2025</th><th data-year="2026" class="tour-col-est">2026E ${TOUR_TAG.est}</th>`
    + `<th data-year="2027" class="tour-col-fc">2027F ${TOUR_TAG.fc}</th><th data-year="2027" class="tour-col-rng">Range 2027F</th>`
    + `<th class="tour-col-chg" title="Change from 2026E to 2027F">2026E → 27F</th></tr></thead>`;
  const row = (name, v25, v26, f, fmt, pts, total) => `<tr${total ? ' class="tour-row-total"' : ''}><td>${esc(name)}</td>`
    + `<td data-year="2025">${v25 == null ? '—' : fmt(v25)}</td><td data-year="2026" class="tour-col-est">${v26 == null ? '—' : fmt(v26)}</td>`
    + `<td data-year="2027" class="tour-col-fc">${fmt(f.base)}</td><td data-year="2027" class="tour-col-rng">${fmt(f.low)}–${fmt(f.high)}</td>`
    + `<td class="tour-col-chg">${tourChange(v26, f.base, pts)}</td></tr>`;
  const table = (id, first, total, rows) => {
    document.getElementById(id).innerHTML = head(first) + '<tbody>' + total + rows.join('') + '</tbody>';
  };
  // a row we have no Kodo figure for: its official 2025 value, then "Not forecast"
  const notRow = (name, v25, fmt) => `<tr class="tour-row-nf"><td>${esc(name)}</td><td data-year="2025">${v25 == null ? '—' : fmt(v25)}</td>`
    + `<td data-year="2026" class="tour-col-est tour-nf">${TOUR_NOT}</td><td data-year="2027" class="tour-col-fc tour-nf">${TOUR_NOT}</td>`
    + `<td data-year="2027" class="tour-col-rng tour-nf">—</td><td class="tour-col-chg">—</td></tr>`;
  const NF = F.not_forecast || {};
  const occFmt = v => (+v).toFixed(0) + '%';
  const sorted = o => Object.entries(o).sort((x, y) => y[1].base - x[1].base);
  table('tour-fc-markets', 'Market',
    row('All markets', tourAnnual('arrivals_total')[2025], N26.arrivals.base, F27.arrivals, tourM, false, true),
    sorted(F.markets_2027).map(([m, v]) => row(m, tourAnnual('arrivals_mkt_' + m)[2025], E26.markets?.[m], v, tourM))
      .concat((NF.markets || []).map(m => notRow(m, tourAnnual('arrivals_mkt_' + m)[2025], tourM))));
  table('tour-fc-cities', 'City',
    row('Morocco', tourAnnual('occupancy_Morocco')[2025], N26.occupancy.base, F27.occupancy, pct, true, true),
    sorted(F.cities_occupancy_2027).map(([c, v]) => row(c, tourAnnual('occupancy_' + c)[2025], E26.cities_occupancy?.[c], v, occFmt, true))
      .concat((NF.cities || []).map(c => notRow(c, tourAnnual('occupancy_' + c)[2025], occFmt))));
  table('tour-fc-airports', 'Airport',
    row('All airports', tourAnnual('air_passengers_total')[2025], N26.air_passengers.base, F27.air_passengers, tourM, false, true),
    sorted(F.airports_2027).map(([a, v]) => row(a, tourAnnual('airport_' + a)[2025], E26.airports?.[a], v, tourM)));

  // Which months of 2026 are official, from the periods the estimate was built on
  const off = E26.official || {};
  const names = { arrivals: 'arrivals', nights: 'nights', receipts: 'travel receipts', air_passengers: 'airport passengers (also by airport)' };
  const bySpan = {};
  Object.keys(names).filter(k => off[k]).forEach(k => (bySpan[tourSpan(off[k])] = bySpan[tourSpan(off[k])] || []).push(names[k]));
  const spans = Object.entries(bySpan).map(([sp, ks]) => `${sp.replace(/ \d{4}$/, '')} for ${ks.join(' and ')}`);
  const held = F.withheld.map(w => esc(w.item)).join('; ');
  document.getElementById('tour-fc-foot').innerHTML =
    (spans.length ? `<span class="tour-fc-months"><strong>2026E</strong>: official figures for ${spans.join(', ')}; `
      + 'the remaining months are Kodo’s model. No official 2026 split by market or city is published yet, so those 2026E figures are Kodo’s.</span> ' : '')
    + 'The range applies to 2027F only; the last column is the change from 2026E to 2027F. '
    + 'Markets include MRE in their country of residence. Airport figures are not backtested, so their range is wider. '
    + `Travel receipts are also forecast by month (chart above). Not forecast: ${held}.`;

  // Catalysts, each from the figures above
  const arr = tourAnnual('arrivals_total'), rec = tourAnnual('receipts_total'), tot = tourAnnual('air_passengers_total');
  const tgt = Object.fromEntries(tourismData.targets.map(t => [t.id, t.value]));
  const mon = {}; tourSeries('receipts_monthly').points.forEach(p => { mon[p.period] = p.value; });
  const mk = id => tourAnnual('arrivals_mkt_' + id);
  const g = (h, y) => tourPct(h[y], h[y - 1]);
  const airYtd = tourSeries('air_passengers_ytd').points[0];
  const cats = [
    ['Roadmap 2023–2026', `Targets for 2026: ${tourM(tgt.arrivals_2026)} arrivals and MAD ${tourB(tgt.receipts_2026)} of receipts. Both passed in 2025: ${tourM(arr[2025])} arrivals and MAD ${tourB(rec[2025])}.`],
    ['2030 vision', `${tourM(tgt.arrivals_2030)} arrivals targeted by 2030, the year Morocco co-hosts the FIFA World Cup with Spain and Portugal.`],
    ['AFCON 2025', `Africa Cup of Nations, 21 Dec 2025 – 18 Jan 2026: travel receipts ${tourSigned(tourPct(mon['2025-12'], mon['2024-12']), 0)}% in December 2025 on a year earlier.`],
    ['Air traffic', `${tourM(tot[2025])} airport passengers in 2025 (${tourSigned(g(tot, 2025), 0)}%), and ${tourSigned(airYtd.yoy_pct)}% in ${tourSpan(airYtd.period)}.`],
    ['Long-haul markets', `Arrivals in 2025: United States ${tourSigned(g(mk('United States'), 2025), 0)}%, Canada ${tourSigned(g(mk('Canada'), 2025), 0)}%, China ${tourSigned(g(mk('China'), 2025), 0)}%.`],
    ['Tourism in the economy', 'Tourism was 7.5% of GDP in 2025, up from 7.2% in 2024 (tourism satellite account).'],
  ];
  document.getElementById('tour-catalysts').innerHTML = cats.map(([t, d]) =>
    `<div class="catalyst-card"><div class="catalyst-card-title">${t}</div><div class="catalyst-card-desc">${esc(d)}</div></div>`).join('');

  // How to read the figures (the source line under it is in the template)
  document.getElementById('tour-notes').textContent = tourismData.notes.join(' ');
}

// Search result → the tourism page with that year selected (2026E or 2027F),
// scrolled to the Outlook section, the year's column briefly highlighted
function showTourismOutlook(year) {
  _srchNavigateToScreen('tourism');
  let tries = 0;
  const go = () => {
    const card = document.getElementById('tour-fc');
    const cells = card ? card.querySelectorAll(`.tour-table [data-year="${year}"]`) : [];
    if (!cells.length || !tourismInited) { if (++tries < 80) setTimeout(go, 100); return; }
    setTourismYear(year === 2026 ? '2026E' : '2027F');
    card.scrollIntoView({ behavior: 'smooth', block: 'start' });
    card.querySelectorAll('.tour-col-flash').forEach(el => el.classList.remove('tour-col-flash'));
    void card.offsetWidth;   // restart the animation if it is already running
    cells.forEach(el => el.classList.add('tour-col-flash'));
    setTimeout(() => cells.forEach(el => el.classList.remove('tour-col-flash')), 2600);
  };
  go();
}

// ─── Pipeline screen ──────────────────────────────────────────────
// One main view (table, cards or map) under a row of filters; black, white
// and grey only (docs/ui-standard.md). A project with no announced opening
// shows "Date not announced" (never a year). A conversion of an operating
// hotel keeps its keys on its card, but they are already counted with that
// hotel, so every new-supply total leaves them out.
const PIPE_NO_DATE = 'Date not announced';
const pipeYear   = p => p.expected_opening || PIPE_NO_DATE;
const pipeNewKeys = p => p.conversion ? 0 : (p.keys || 0);
const pipeConversionLine = p => p.conversion
  ? `<div class="pipe-card-conversion">Conversion of ${fmt.esc(p.converts_hotel_name || 'an operating hotel')} · keys already counted</div>` : '';
// The project's brand group in the Brands page's logo tile: a local logo
// file or the group's initials tile (never a remote image), or a neutral
// "?" tile when no group is stored. Brand and tile open the group's page on
// Brands when it has one (operating hotels); otherwise they are plain text.
const PIPE_NO_GROUP = new Set(['', 'Undisclosed', 'Unknown', 'None', 'N/A']);
function pipeBrandGroup(p) {
  const bg = String(p.brand_group || '').trim();
  return PIPE_NO_GROUP.has(bg) ? '' : bg;
}
const pipeHasBrandPage = bg => !!bg && Array.isArray(hotels) && hotels.some(h => h.brand_group === bg);
function pipeBrandTile(bg, size) {
  if (!bg) return initialsTile('?', size, 6, 'var(--bg-alt)', 'var(--text-3)');
  if (LOCAL_BRAND_LOGOS[bg]) return logoChipImg(LOCAL_BRAND_LOGOS[bg], bg, size, 6, brandInitials(bg, size, 6));
  const custom = BRAND_CUSTOM_LOGOS[bg];
  if (custom) return initialsTile(custom.letter, size, 6, custom.bg, custom.color);
  return brandInitials(bg, size, 6);
}
function pipeBrandHtml(p, size) {
  // The group's name as the Brands page shows it; the stored brand (e.g.
  // "Ritz Carlton") only in the hover title
  const bg = pipeBrandGroup(p), label = fmt.esc(bg || 'Brand not stored');
  const tip = p.brand && p.brand !== bg ? ` title="${fmt.esc(p.brand)}"` : '';
  if (!pipeHasBrandPage(bg)) return `<span class="pipe-brand"${tip}>${pipeBrandTile(bg, size)}<span>${label}</span></span>`;
  return `<button type="button" class="pipe-brand pipe-brand-link" data-brand-group="${fmt.esc(bg)}"${tip}`
    + ` aria-label="${label}${tip ? ' (' + fmt.esc(p.brand) + ')' : ''}: open on Brands" onclick="pipeOpenBrand(event, this)">${pipeBrandTile(bg, size)}<span>${label}</span>`
    + `<span class="pipe-brand-arrow" aria-hidden="true">→</span></button>`;
}
function pipeOpenBrand(e, el) {
  e.stopPropagation();                               // the card, row or marker keeps its own click
  if (activeInfoWindow) activeInfoWindow.close();
  showBrandDetail(el.dataset.brandGroup, document.getElementById('screen-hotel').classList.contains('active') ? 'hotel' : 'pipeline');
}
// Keys per group (opening year or city), new rooms only
function pipeKeysBy(data, key) {
  const t = {};
  data.forEach(p => { if (pipeNewKeys(p)) { const k = key(p); t[k] = (t[k] || 0) + pipeNewKeys(p); } });
  return t;
}

// Stage: the project's status, plus "Opening soon" (an announced opening year
// within the next 12 months, to the year: openings are announced as a year)
const pipeSoonYear = () => new Date(Date.now() + 365 * 864e5).getFullYear();
const pipeIsSoon = p => p.status !== 'Opened' && !!p.expected_opening && p.expected_opening <= pipeSoonYear();
function pipeMatchesStage(p, stage) {
  return stage === 'all' || (stage === 'soon' ? pipeIsSoon(p) : p.status === stage);
}

const PIPE_VIEWS = ['table', 'cards'];   // the map is always shown, under the view
function pipeSavedView() {
  try { const v = localStorage.getItem('kodo.pipeline.view'); return PIPE_VIEWS.includes(v) ? v : 'table'; } catch { return 'table'; }
}

async function initPipeline() {
  if (pipelineInited) {
    if (googlePipelineMap) setTimeout(() => google.maps.event.trigger(googlePipelineMap, 'resize'), 60);
    else setTimeout(initPipelineMap, 60);
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
  fetch('/api/pipeline/updated').then(r => r.ok ? r.json() : null).then(d => {
    if (d && d.updated) document.getElementById('pipe-line').textContent =
      `Hotel projects announced or under construction in Morocco, not yet open. Updated ${pipeDay(d.updated)}.`;
  }).catch(() => {});

  const cities = [...new Set(pipelineData.map(p => p.city))].sort((a, b) => dn(a).localeCompare(dn(b)));
  const groups = [...new Set(pipelineData.map(pipeBrandGroup).filter(Boolean))].sort();
  const cityEl = document.getElementById('pipe-city-filter');
  const grpEl  = document.getElementById('pipe-group-filter');
  cities.forEach(c => cityEl.add(new Option(dn(c), c)));
  groups.forEach(g => grpEl.add(new Option(g, g)));

  renderPipelineKPIs();
  pipeSetView(pipeSavedView(), false);
  applyPipelineFilter();
  setTimeout(initPipelineMap, 60);
}

const pipeDay = iso => new Date(iso + 'T00:00:00').toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });

function filteredPipeline() {
  const q = fold(pipelineState.q.trim());
  return pipelineData.filter(p =>
    pipeMatchesStage(p, pipelineState.stage) &&
    (pipelineState.city  === 'all' || p.city === pipelineState.city) &&
    (pipelineState.group === 'all' || pipeBrandGroup(p) === pipelineState.group) &&
    (!q || fold(`${p.name || ''} ${p.brand || ''} ${p.brand_group || ''} ${p.city || ''} ${dn(p.city || '')}`).includes(q)));
}

// Summary: counts only (projects, new keys, opening within 12 months, under construction)
function renderPipelineKPIs() {
  const all = pipelineData;
  const set = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
  set('pkpi-total', all.length);
  set('pkpi-keys', all.reduce((s, p) => s + pipeNewKeys(p), 0).toLocaleString('en'));
  const noKeys = all.filter(p => !p.keys && !p.conversion).length;
  set('pkpi-keys-line', noKeys ? `${noKeys} project${noKeys !== 1 ? 's' : ''} with no room count yet` : ' ');
  const y = pipeSoonYear();
  set('pkpi-soon', all.filter(pipeIsSoon).length);
  set('pkpi-soon-line', `announced for ${y - 1}–${y}`);
  document.getElementById('pkpi-soon-tip').dataset.tip =
    `Projects with an announced opening year up to ${y}: the next 12 months, to the year, since openings are announced as a year. Projects with no date announced are not counted.`;
  set('pkpi-uc', all.filter(p => p.status === 'Under Construction').length);
  const counts = { all: all.length, Planning: 0, 'Under Construction': 0, soon: 0, Opened: 0 };
  all.forEach(p => { if (p.status in counts) counts[p.status]++; if (pipeIsSoon(p)) counts.soon++; });
  document.querySelectorAll('#pipe-stage [data-stage]').forEach(b => {
    const n = counts[b.dataset.stage] || 0;
    b.disabled = !n && b.dataset.stage !== 'all';
    b.title = n ? '' : 'No project at this stage';
  });
}

// Stage: black = under construction, outlined = planning, grey = opened / other
function pipeStagePill(p) {
  if (p.status === 'Under Construction') return '<span class="k-pill k-pill--solid">Under construction</span>';
  if (p.status === 'Planning') return '<span class="k-pill">Planning</span>';
  return `<span class="k-pill k-pill--muted">${fmt.esc(p.status || 'Other')}</span>`;
}
const pipeKeysText = p => p.keys ? p.keys.toLocaleString('en') : 'TBC';
const pipeInvText  = p => p.investment_mad ? Math.round(p.investment_mad / 1e6).toLocaleString('en') : 'TBC';

function pipeSorted(data) {
  const { col, dir } = pipelineSort;
  const val = p => col === 'category' ? (SEGMENT_ORDER_JS.indexOf(p.category) + 1 || 99)
    : col === 'city' ? dn(p.city || '') : col === 'name' ? (p.name || '') : col === 'status' ? (p.status || '') : p[col];
  return [...data].sort((a, b) => {
    const av = val(a), bv = val(b);
    if (av == null || bv == null || av === '' || bv === '') return (av == null || av === '') - (bv == null || bv === '') || (a.name || '').localeCompare(b.name || '');
    const c = typeof av === 'string' ? av.localeCompare(bv) : av - bv;
    return dir * c || (a.name || '').localeCompare(b.name || '');
  });
}
const SEGMENT_ORDER_JS = ['Ultra Luxury', 'Luxury', 'Upper Upscale', 'Upscale', 'Upper Midscale', 'Midscale', 'Economy'];

const pipeSelClass = p => String(p.id) === String(pipeSelectedId) ? ' class="is-selected"' : '';
function renderPipelineTableView(data) {
  const tbody = document.getElementById('pipeline-tbody');
  if (!data.length) { tbody.innerHTML = '<tr><td colspan="7" class="k-empty">No project matches these filters.</td></tr>'; return; }
  tbody.innerHTML = pipeSorted(data).map(p => `<tr data-pid="${fmt.esc(String(p.id))}" tabindex="0" title="Show on the map"${pipeSelClass(p)}>
      <td class="pipe-proj">
        <span class="pipe-proj-name">${fmt.esc(p.name)}</span>
        <span class="pipe-proj-brand">${pipeBrandHtml(p, 16)}</span>
        <span class="pipe-proj-m">${fmt.esc(dn(p.city || ''))}</span>
        ${pipeConversionLine(p)}
      </td>
      <td class="col-hide-mobile">${fmt.esc(dn(p.city || ''))}</td>
      <td class="col-hide-mobile">${fmt.esc(p.category || '—')}</td>
      <td>${pipeStagePill(p)}</td>
      <td class="num">${p.expected_opening || '<span class="pipe-tba" title="' + PIPE_NO_DATE + '">TBA</span>'}</td>
      <td class="num">${pipeKeysText(p)}</td>
      <td class="num col-hide-mobile pipe-inv">${pipeInvText(p)}</td>
    </tr>`).join('');
}

function renderPipelineCards(data) {
  const grid = document.getElementById('pipe-cards-grid');
  if (!data.length) { grid.innerHTML = '<p class="k-empty">No project matches these filters.</p>'; return; }
  grid.innerHTML = pipeSorted(data).map(p => `<div class="pipe-card2${String(p.id) === String(pipeSelectedId) ? ' is-selected' : ''}" data-pid="${fmt.esc(String(p.id))}" tabindex="0" title="Show on the map">
      <div class="pipe-card2-top"><span class="pipe-proj-name">${fmt.esc(p.name)}</span>${pipeStagePill(p)}</div>
      <div class="pipe-proj-brand">${pipeBrandHtml(p, 16)}</div>
      <div class="pipe-card2-meta">${fmt.esc(dn(p.city || ''))}${p.category ? ' · ' + fmt.esc(p.category) : ''}</div>
      ${pipeConversionLine(p)}
      <dl class="pipe-card2-nums">
        <div><dt>Opening</dt><dd>${fmt.esc(String(pipeYear(p)))}</dd></div>
        <div><dt>Keys</dt><dd>${pipeKeysText(p)}</dd></div>
        <div><dt>Inv. (MAD M)</dt><dd>${pipeInvText(p)}</dd></div>
      </dl>
    </div>`).join('');
}

function pipeSetView(view, save = true) {
  pipelineState.view = view;
  document.querySelectorAll('#pipe-view [data-view]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.view === view)));
  document.querySelectorAll('#screen-pipeline [data-pview]').forEach(v => { v.hidden = v.dataset.pview !== view; });
  if (save) try { localStorage.setItem('kodo.pipeline.view', view); } catch { /* private window */ }
}

function applyPipelineFilter() {
  const data = filteredPipeline();
  const el = document.getElementById('pipe-count');
  if (el) el.textContent = `${data.length} project${data.length !== 1 ? 's' : ''}`;
  renderPipelineTableView(data);
  renderPipelineCards(data);
  const onMap = data.filter(p => p.lat != null && p.lng != null).length;
  const mc = document.getElementById('pipe-map-count');
  if (mc) mc.textContent = `Map · ${onMap} project${onMap !== 1 ? 's' : ''}`;
  if (googlePipelineMap) {
    const ids = new Set(data.map(p => p.id));
    if (pipeSelectedId != null && !ids.has(pipeSelectedId)) pipeCloseSelected();
    pipelineMarkers.forEach(({ marker, project }) => marker.setMap(ids.has(project.id) ? googlePipelineMap : null));
  }
}

// Map: the open project black (white in dark), the others grey: dark grey
// under construction, light grey planning. No blue.
let pipeSelectedId = null;
function pipeMarkerIcon(p) {
  const cs = getComputedStyle(document.documentElement);
  const sel = String(p.id) === String(pipeSelectedId);
  const color = sel ? cs.getPropertyValue('--text').trim()
    : p.status === 'Under Construction' ? cs.getPropertyValue('--text-2').trim() : cs.getPropertyValue('--text-3').trim();
  return { path: google.maps.SymbolPath.CIRCLE, scale: Math.max(8, Math.sqrt(p.keys || 0) * 0.85) + (sel ? 2 : 0),
           fillColor: color, fillOpacity: sel ? 1 : 0.8, strokeColor: cs.getPropertyValue('--bg').trim(), strokeWeight: sel ? 2 : 1 };
}
function pipeRestyleMarkers() {
  if (googlePipelineMap) pipelineMarkers.forEach(({ marker, project }) => marker.setIcon(pipeMarkerIcon(project)));
}
// The selected project: black marker, highlighted row / card (no scrolling)
function pipeMarkSelected() {
  document.querySelectorAll('#screen-pipeline [data-pid]').forEach(el =>
    el.classList.toggle('is-selected', el.dataset.pid === String(pipeSelectedId)));
}
function pipeCloseSelected() {
  if (activeInfoWindow) activeInfoWindow.close();
  pipeSelectedId = null; pipeRestyleMarkers(); pipeMarkSelected();
}
function pipeOpenOnMap(p, marker) {
  if (activeInfoWindow) activeInfoWindow.close();
  pipeSelectedId = p.id; pipeRestyleMarkers(); pipeMarkSelected();
  activeInfoWindow = new google.maps.InfoWindow({ content: pipelinePopupHTML(p) });
  activeInfoWindow.addListener('closeclick', () => { pipeSelectedId = null; pipeRestyleMarkers(); pipeMarkSelected(); });
  activeInfoWindow.open({ map: googlePipelineMap, anchor: marker, shouldFocus: false });
}

function initPipelineMap(then) {
  const container = document.getElementById('pipeline-map-container');
  if (!container || !googleMapsApiReady || googlePipelineMap || !pipelineData) return;
  try {
    googlePipelineMap = new google.maps.Map(container, {
      ...GMAP_OPTIONS_BASE,
      center: { lat: 31.5, lng: -5.5 },
      zoom:   6,
      styles: gmapStyles(),
    });
    const ids = new Set(filteredPipeline().map(p => p.id));
    pipelineMarkers = pipelineData.filter(p => p.lat != null && p.lng != null).map(p => {
      const marker = new google.maps.Marker({ position: { lat: p.lat, lng: p.lng }, map: ids.has(p.id) ? googlePipelineMap : null,
                                              icon: pipeMarkerIcon(p), title: p.name });
      marker.addListener('click', () => pipeOpenOnMap(p, marker));
      return { marker, project: p };
    });
    if (then) then();
  } catch (e) {
    console.error('Google Maps pipeline init failed:', e);
  }
}

// Row or card click ("Show on the map"): scroll to the map, centre it on the
// project and open its pop-up
function pipeShowProject(id) {
  const card = document.getElementById('pipe-map-card');
  if (card) card.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'center' });
  const open = () => {
    const m = pipelineMarkers.find(x => String(x.project.id) === String(id));
    if (!m) return;
    if (!m.marker.getMap()) m.marker.setMap(googlePipelineMap);
    googlePipelineMap.setCenter(m.marker.getPosition());
    if (googlePipelineMap.getZoom() < 8) googlePipelineMap.setZoom(8);
    pipeOpenOnMap(m.project, m.marker);
  };
  if (googlePipelineMap) open(); else initPipelineMap(open);
}

function pipelinePopupHTML(p) {
  const inv = p.investment_mad ? 'MAD ' + (p.investment_mad / 1e9).toFixed(2) + 'B' : 'TBC';
  return `<div class="hiq-popup">
    <div class="hiq-popup-name">${fmt.esc(p.name)}</div>
    <div class="hiq-popup-meta">${pipeBrandHtml(p, 14)}</div>
    <div class="hiq-popup-meta">${fmt.esc(dn(p.city || ''))}${p.category ? ' · ' + fmt.esc(p.category) : ''}</div>
    ${p.conversion ? `<div class="hiq-popup-meta">Conversion of ${fmt.esc(p.converts_hotel_name || 'an operating hotel')} · keys already counted</div>` : ''}
    <div class="hiq-popup-grid">
      <div class="hiq-popup-stat"><div class="hiq-popup-stat-val">${p.keys || 'TBC'}</div><div class="hiq-popup-stat-lbl">Keys</div></div>
      <div class="hiq-popup-stat"><div class="hiq-popup-stat-val">${fmt.esc(String(pipeYear(p)))}</div><div class="hiq-popup-stat-lbl">Opening</div></div>
      <div class="hiq-popup-stat"><div class="hiq-popup-stat-val">${inv}</div><div class="hiq-popup-stat-lbl">Investment</div></div>
      <div class="hiq-popup-stat"><div class="hiq-popup-stat-val">${pipeStagePill(p)}</div><div class="hiq-popup-stat-lbl">Stage</div></div>
    </div>
  </div>`;
}

// Pipeline events (delegation on the screen)
document.getElementById('screen-pipeline').addEventListener('click', e => {
  const st = e.target.closest('#pipe-stage [data-stage]');
  if (st && !st.disabled) {
    pipelineState.stage = st.dataset.stage;
    document.querySelectorAll('#pipe-stage [data-stage]').forEach(b => b.setAttribute('aria-pressed', String(b === st)));
    applyPipelineFilter();
    return;
  }
  const vw = e.target.closest('#pipe-view [data-view]');
  if (vw) { pipeSetView(vw.dataset.view); return; }
  const th = e.target.closest('th[data-psort]');
  if (th) {
    const col = th.dataset.psort;
    pipelineSort.dir = pipelineSort.col === col ? -pipelineSort.dir : (['keys', 'investment_mad'].includes(col) ? -1 : 1);
    pipelineSort.col = col;
    document.querySelectorAll('#pipeline-table th[data-psort]').forEach(t => t.removeAttribute('aria-sort'));
    th.setAttribute('aria-sort', pipelineSort.dir === 1 ? 'ascending' : 'descending');
    applyPipelineFilter();
    return;
  }
  const row = e.target.closest('[data-pid]');
  if (row && !e.target.closest('a, button')) pipeShowProject(row.dataset.pid);
});
document.getElementById('screen-pipeline').addEventListener('keydown', e => {
  const row = e.target.closest && e.target.closest('[data-pid]');
  if (row && e.target === row && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); pipeShowProject(row.dataset.pid); }
});
document.getElementById('pipe-city-filter').addEventListener('change', e => { pipelineState.city = e.target.value; applyPipelineFilter(); });
document.getElementById('pipe-group-filter').addEventListener('change', e => { pipelineState.group = e.target.value; applyPipelineFilter(); });
document.getElementById('pipe-search').addEventListener('input', e => { pipelineState.q = e.target.value; applyPipelineFilter(); });

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

// News category families — same colour families as Owners' portfolio
// types and Events' types (see FAMILY_INDEX above and
// KodoEvents.TYPE_FAMILY in events.js). Keys are the real `category` values seen in news.json; anything
// else falls back to grey. Sponsored articles use sky for "Partner".
const NEWS_CATEGORY_FAMILY = {
  'Market Intelligence': 'blue',
  'Pipeline':            'green',
  'Openings':            'orange',
  'Interviews':          'violet',
};

function edCatPill(cat, type) {
  const isSponsored = type === 'sponsored' || type === 'partner';
  if (isSponsored) return pillHtml('sky', 'Partner', 'ed-cat-badge ed-cat-partner');
  return pillHtml(NEWS_CATEGORY_FAMILY[cat] || 'grey', cat || '', 'ed-cat-badge');
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
            <span class="ed-featured-badge pill--solid">FEATURED</span>
            ${edCatPill(f.category, f.type)}
          </div>
          <h2 class="ed-hero-title">${fmt.esc(f.title || f.headline || '')}</h2>
          <p class="ed-hero-excerpt">${fmt.esc(f.excerpt || f.summary || '')}</p>
          <div class="ed-hero-meta">
            <span>${fmt.esc(f.author || 'Kodo Editorial')}</span>
            <span class="ed-dot">·</span>
            <span>${newsDateFmt(f.date)}</span>
            <span class="ed-dot">·</span>
            <span>${fmt.esc(f.read_time || '')}</span>
          </div>
          <button class="ed-read-btn" data-art-id="${f.id}">Read article →</button>
        </div>
        <div class="ed-hero-img-wrap">
          <img src="${newsCoverUrl(f.slug, f.cover_image_query)}" alt="${fmt.esc(f.title || '')}"
               class="ed-hero-img" loading="lazy" onerror="this.onerror=null;this.src='/static/images/news-placeholder.svg'">
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
        <div class="ed-spons-badge pill--sky">Partner</div>
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
    grid.innerHTML = (newsData.all || []).length ? '<p class="news-loading">No articles in this category yet.</p>'
      : '<p class="news-loading">No articles yet. Kodo’s market notes will be published here.</p>';
    loadBtn.style.display = 'none';
    return;
  }

  grid.innerHTML = shown.map(a => {
    const isSponsored = a.type === 'sponsored' || a.type === 'partner';
    return `<div class="ed-card ${isSponsored ? 'ed-card-sponsored' : ''}" data-art-id="${a.id}">
      <div class="ed-card-img-wrap">
        <img src="${newsCoverUrl(a.slug, a.cover_image_query)}"
             alt="${fmt.esc(a.title || a.headline || '')}" class="ed-card-img" loading="lazy"
             onerror="this.onerror=null;this.src='/static/images/news-placeholder.svg'">
      </div>
      <div class="ed-card-body">
        ${edCatPill(a.category, a.type)}
        <div class="ed-card-title">${fmt.esc(a.title || a.headline || '')}</div>
        <div class="ed-card-excerpt">${fmt.esc(a.excerpt || a.summary || '')}</div>
        <div class="ed-card-footer">
          <span>${fmt.esc(a.author || 'Kodo Editorial')}</span>
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
    `<span class="art-author">${fmt.esc(art.author || 'Kodo Editorial')}</span>
     <span class="ed-dot">·</span>
     <span>${newsDateFmt(art.date)}</span>
     <span class="ed-dot">·</span>
     <span>${fmt.esc(art.read_time || '')}</span>`;

  document.getElementById('art-cover').innerHTML =
    `<img src="${newsCoverUrl(art.slug, art.cover_image_query)}"
          alt="${fmt.esc(art.title || '')}" class="art-cover-img" loading="lazy"
          onerror="this.onerror=null;this.src='/static/images/news-placeholder.svg'">`;

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
  const body = document.querySelector('.app-body');
  body.classList.toggle('no-sidebar', !SIDEBAR_SCREENS.has(screen));
  body.dataset.screen = screen;                    // the segment filter shows on the Map page only
}

// ─── Mobile nav ───────────────────────────────────────────────────

function closeMobileNav() {
  const overlay = document.getElementById('mobileMenuOverlay');
  const btn     = document.getElementById('mobileMenuBtn');
  if (!overlay || !btn) return;
  overlay.classList.remove('lp-overlay-open');
  btn.classList.remove('lp-menu-open');
  btn.setAttribute('aria-expanded', 'false');
  document.body.style.overflow = '';
  setTimeout(() => { overlay.style.display = 'none'; }, 350);
}

function openMobileNav() {
  const overlay = document.getElementById('mobileMenuOverlay');
  const btn     = document.getElementById('mobileMenuBtn');
  if (!overlay || !btn) return;
  overlay.style.display = 'block';
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      overlay.classList.add('lp-overlay-open');
      btn.classList.add('lp-menu-open');
      btn.setAttribute('aria-expanded', 'true');
      document.body.style.overflow = 'hidden';
    });
  });
}

// A new screen or profile opens at the top, not at the previous one's scroll position
function scrollMainToTop() {
  const m = document.querySelector('.main-content');
  if (m) m.scrollTop = 0;
}

function syncMobileNav(screen) {
  document.querySelectorAll('.mobile-menu-link').forEach(l =>
    l.classList.toggle('active', l.dataset.screen === screen)
  );
}

document.getElementById('mobileMenuBtn').addEventListener('click', () => {
  const overlay = document.getElementById('mobileMenuOverlay');
  overlay.classList.contains('lp-overlay-open') ? closeMobileNav() : openMobileNav();
});

document.getElementById('mobileMenuClose').addEventListener('click', closeMobileNav);

document.getElementById('mobileMenuOverlay').addEventListener('click', e => {
  if (e.target.id === 'mobileMenuOverlay') closeMobileNav();
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
    scrollMainToTop();

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
    if (screen === 'benchmarking') initBenchmarking();
    if (screen === 'reports') initReports();
    if (screen === 'owners')  initOwners();
    if (screen === 'valuation') initValuation();
  });
});

// Market Overview scope: destination tabs, the comparison table, "Compare with Morocco", the sidebar number
document.getElementById('dash-scope').addEventListener('click', e => {
  const b = e.target.closest('[data-tab]');
  if (b) selectTab(b.dataset.tab);
});
document.getElementById('dash-scope').addEventListener('keydown', e => {   // arrow keys between tabs
  if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
  const i = DASH_TABS.indexOf(state.tab) + (e.key === 'ArrowRight' ? 1 : -1);
  const t = DASH_TABS[(i + DASH_TABS.length) % DASH_TABS.length];
  selectTab(t);
  document.querySelector(`#dash-scope [data-tab="${t}"]`).focus();
});
document.getElementById('dest-table').addEventListener('click', e => {
  const th = e.target.closest('th[data-sort]');
  if (th) { sortDestTable(th.dataset.sort); return; }
  const tr = e.target.closest('tr[data-city]');
  if (tr) selectCity(tr.dataset.city);
});
document.getElementById('dest-table').addEventListener('keydown', e => {
  const tr = e.target.closest('tr[data-city]');
  if (tr && e.key === 'Enter') selectCity(tr.dataset.city);
});
document.getElementById('dash-brands-link').addEventListener('click', e => {
  e.preventDefault();
  document.querySelector('.nav-link[data-screen="brands"]').click();
});
document.querySelectorAll('.dest-metric-btn').forEach(b => b.addEventListener('click', () => setDestMetric(b.dataset.metric)));

// Logo click → navigate to Dashboard
document.getElementById('navbar-logo').addEventListener('click', () => {
  document.querySelector('.nav-link[data-screen="dashboard"]').click();
});

// Destination list (sidebar): click, arrow keys and Enter, search
document.getElementById('city-filter').addEventListener('click', e => {
  const item = e.target.closest('.dest-row');
  if (item) selectCity(item.dataset.city);
});
document.getElementById('city-filter').addEventListener('keydown', e => {
  const rows = [...document.querySelectorAll('#city-filter .dest-row')].filter(li => !li.hidden);
  const i = rows.indexOf(document.activeElement);
  if (i < 0) return;
  const go = j => { e.preventDefault(); const r = rows[Math.max(0, Math.min(rows.length - 1, j))]; rows.forEach(x => { x.tabIndex = -1; }); r.tabIndex = 0; r.focus({ preventScroll: false }); };
  if (e.key === 'ArrowDown') go(i + 1);
  else if (e.key === 'ArrowUp') { if (i === 0) { e.preventDefault(); document.getElementById('dest-search').focus(); } else go(i - 1); }
  else if (e.key === 'Home') go(0);
  else if (e.key === 'End') go(rows.length - 1);
  else if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); selectCity(rows[i].dataset.city); rows[i].focus(); }
});
['dest-search', 'dest-search-m'].forEach(id => {
  const inp = document.getElementById(id);
  if (!inp) return;
  inp.addEventListener('input', () => {
    const other = document.getElementById(id === 'dest-search' ? 'dest-search-m' : 'dest-search');
    if (other) other.value = inp.value;
    filterDestRows();
  });
  inp.addEventListener('keydown', e => {
    if (e.key === 'ArrowDown' && id === 'dest-search') {
      const first = [...document.querySelectorAll('#city-filter .dest-row')].find(li => !li.hidden);
      if (first) { e.preventDefault(); first.tabIndex = 0; first.focus(); }
    }
    if (e.key === 'Enter') {
      const hit = [...document.querySelectorAll(id === 'dest-search' ? '#city-filter .dest-row:not(.dest-row--all)' : '#mobile-city-pills [data-mcity]:not([data-mcity="all"])')].find(x => !x.hidden);
      if (hit) { e.preventDefault(); selectCity(hit.dataset.city || hit.dataset.mcity); }
    }
  });
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

// Hotels: one filter row (search, destination, segment, owner, sort), sortable headers, row click
document.getElementById('hotels-search').addEventListener('input', e => {
  hotelsState.query = e.target.value;
  renderHotelsTable();
});
document.getElementById('hotels-city-select').addEventListener('change', e => {
  hotelsState.city = e.target.value;
  renderHotelsTable();
});
document.getElementById('hotels-seg').addEventListener('click', e => {
  const b = e.target.closest('[data-hseg]');
  if (!b) return;
  hotelsState.seg = b.dataset.hseg;
  syncHotelsSeg();
  renderHotelsTable();
});
document.getElementById('hotels-sort-select').addEventListener('change', e => {
  const val = e.target.value;
  hotelsState.col = val;
  hotelsState.dir = STRING_COLS.has(val) ? 1 : -1;
  renderHotelsTable();
});
document.getElementById('hotels-owner-select').addEventListener('change', e => {
  hotelsState.owner = e.target.value;
  renderHotelsTable();
});
document.getElementById('hotels-table').addEventListener('click', e => {
  const brand = e.target.closest('.k-brand-link');
  if (brand) { e.stopPropagation(); showBrandDetail(brand.dataset.brandGroup, brand.dataset.from); return; }
  const th = e.target.closest('th[data-col]');
  if (th) {
    const col = th.dataset.col;
    if (col === hotelsState.col) hotelsState.dir *= -1;
    else { hotelsState.col = col; hotelsState.dir = STRING_COLS.has(col) ? 1 : -1; }
    renderHotelsTable();
    return;
  }
  const row = e.target.closest('tr[data-hid]');
  if (row) showHotelDetail(+row.dataset.hid);
});
document.getElementById('hotels-table').addEventListener('keydown', e => {
  const row = e.target.closest && e.target.closest('tr[data-hid]');
  if (row && e.target === row && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); showHotelDetail(+row.dataset.hid); }
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
  const th = e.target.closest('th[data-bcol]');
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

// Brands: row or card opens the brand page; the Pipeline cell opens the Pipeline filtered on the group
function brandsOpen(e) {
  const pipe = e.target.closest('[data-pipe-group]');
  if (pipe) { e.stopPropagation(); openPipelineForGroup(pipe.dataset.pipeGroup); return true; }
  if (e.target.closest('[data-tip], .kodo-badge')) return true;            // a tooltip, not the row
  const row = e.target.closest('[data-brand-group]');
  if (row) { showBrandDetail(row.dataset.brandGroup, 'brands'); return true; }
  return false;
}
document.getElementById('brands-cards-grid').addEventListener('click', brandsOpen);
document.getElementById('brands-comp-tbody').addEventListener('click', brandsOpen);
document.getElementById('screen-brands').addEventListener('keydown', e => {
  const row = e.target.closest && e.target.closest('[data-brand-group]');
  if (row && e.target === row && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); showBrandDetail(row.dataset.brandGroup, 'brands'); }
});
document.getElementById('brands-comp-table').addEventListener('click', e => {
  const th = e.target.closest('th[data-bccol]');
  if (!th) return;
  const col = th.dataset.bccol;
  if (col === brandsFilter.sort) brandsFilter.dir *= -1;
  else { brandsFilter.sort = col; brandsFilter.dir = BRANDS_STR_COLS.has(col) ? 1 : -1; }
  if (brandsInited) renderBrands();
});
document.getElementById('brands-seg-pills').addEventListener('click', e => {
  const btn = e.target.closest('[data-bseg]');
  if (!btn) return;
  document.querySelectorAll('#brands-seg-pills [data-bseg]').forEach(b => b.setAttribute('aria-pressed', String(b === btn)));
  brandsFilter.segment = btn.dataset.bseg;
  if (brandsInited) renderBrands();
});
document.getElementById('brands-search').addEventListener('input', e => {
  brandsFilter.search = e.target.value;
  if (brandsInited) renderBrands();
});
document.getElementById('brands-sort').addEventListener('change', e => {
  brandsFilter.sort = e.target.value;
  brandsFilter.dir = BRANDS_STR_COLS.has(e.target.value) ? 1 : -1;
  if (brandsInited) renderBrands();
});
document.getElementById('brands-view').addEventListener('click', e => {
  const b = e.target.closest('[data-view]');
  if (b) brandsSetView(b.dataset.view);
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
    label.textContent = 'Kodo Analyst';
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

// Hotels filter row: the destination select (with counts) and the segment counts
function buildCityPills() {
  const all = hotels || [];
  const sel = document.getElementById('hotels-city-select');
  const cities = [...new Set(all.map(h => h.city))].sort((a, b) => dn(a).localeCompare(dn(b)));
  const keep = cities.includes(sel.value) ? sel.value : 'all';
  sel.replaceChildren(new Option('All destinations', 'all'),
    ...cities.map(c => new Option(`${dn(c)} (${all.filter(h => h.city === c).length})`, c)));
  sel.value = keep;
}

function buildSegPills() {
  const all = hotels || [];
  document.querySelectorAll('#hotels-seg [data-hseg]').forEach(b => {
    const seg = b.dataset.hseg;
    b.title = `${seg === 'all' ? all.length : all.filter(h => h.category === seg).length} hotels`;
  });
}

// Under 768 px the list is a row of chips (ranked like the list)
function buildMobileCityPills(rows) {
  const bar = document.getElementById('mobile-city-pills');
  const on = c => c === state.city;
  bar.innerHTML = `<button type="button" class="dest-chip${on('all') ? ' active' : ''}" data-mcity="all" aria-pressed="${on('all')}">All Morocco</button>`
    + (rows || sidebarCities()).map(c => `<button type="button" class="dest-chip${on(c.city) ? ' active' : ''}" data-mcity="${escAttr(c.city)}" aria-pressed="${on(c.city)}">`
      + `${fmt.esc(dn(c.city))}<span class="dest-chip-val">${state.destMetric === 'occ' ? (c.occupancy == null ? '' : (c.occupancy * 100).toFixed(1) + '%')
        : c.bar.val == null ? '' : c.bar.limited ? KodoBar.LIMITED : fmt.mad(c.bar.val)}</span></button>`).join('');
  filterDestRows();
}

// Mobile city filter
document.getElementById('mobile-city-pills').addEventListener('click', e => {
  const btn = e.target.closest('[data-mcity]');
  if (btn) selectCity(btn.dataset.mcity);
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

// ─── Benchmarking ─────────────────────────────────────────────────
// Benchmarker and Advisory plans: the rate benchmark of the organisation's
// comp set (below). There is no sample or demo mode: without the plan, or
// before a comp set is chosen, the page says what to do instead.

let benchmarkInited = false;
async function initBenchmarking() {
  if (benchmarkInited) return;
  benchmarkInited = true;
  await initRateBenchmark();
}

// Calendar heat: published rate = blue, modelled occupancy = green
function adrCellStyle(adr, isCompSet = false) {
  if (isCompSet) {
    if (adr >= 6000) return heatCell('grey', 3, '600');
    if (adr >= 4000) return heatCell('grey', 2, '500');
    return heatCell('grey', 1);
  }
  if (adr >= 6000) return heatCell('blue', 3, '600');
  if (adr >= 4000) return heatCell('blue', 2, '500');
  if (adr >= 2000) return heatCell('blue', 1);
  return heatCell('blue', 0);
}

function occCellStyle(occ, isCompSet = false) {
  const p = occ * 100;
  if (isCompSet) {
    if (p >= 80) return heatCell('grey', 3, '600');
    if (p >= 60) return heatCell('grey', 2, '500');
    return heatCell('grey', 1);
  }
  if (p >= 80) return heatCell('green', 3, '600');
  if (p >= 60) return heatCell('green', 2, '500');
  if (p >= 40) return heatCell('green', 1);
  return heatCell('green', 0);
}

// ─── Benchmarking: rate benchmark (real mode) ─────────────────────
// Benchmarker and Advisory plans with a comp set see the rate benchmark:
// published rates (scraped_rates.csv) and modelled occupancy
// (estimated_occupancy.csv) for the next 30 nights. No achieved rate,
// occupancy or Rooms RevPAR exists for these hotels, so none is shown. Everyone
// else sees what to do instead: the plans, or setting up the comp set.

const rbState = {
  canReal: false,        // plan allows the rate benchmark
  compSet: null,         // { subject_id, comp_ids } of the organisation
  data: null,            // /api/benchmarking/rates
  editing: false,
  draftSubject: null, draftComps: [],
  rateCal: null, occCal: null,   // { y, m } shown by each calendar
  past: {}, pastLoading: {}, pastFirst: null,   // past months of the rate calendar (last published rates)
};

const rbHotel = id => (hotels || []).find(h => String(h.id) === String(id));
const rbMad   = v => v == null ? '–' : 'MAD ' + Math.round(v).toLocaleString('en');
const rbShort = v => v == null ? '–' : Math.round(v).toLocaleString('en');
// Price coverage label (full | partial | none | mixed) from a level
const rbConf  = c => ({ high: 'full', medium: 'partial', low: 'none', mixed: 'mixed' })[c] || c || '';

async function initRateBenchmark() {
  const me = window._kodoUser || await fetch('/api/me').then(r => r.ok ? r.json() : {}).catch(() => ({}));
  rbState.canReal = me.tier === 'benchmarker' || me.tier === 'advisory';
  if (rbState.canReal) {
    const cs = await fetch('/api/benchmarking/compset').then(r => r.ok ? r.json() : {}).catch(() => ({}));
    rbState.compSet = cs.comp_set || null;
    if (rbState.compSet) await loadRateBenchmark();
  }
  applyBenchMode();
}

async function loadRateBenchmark() {
  rbState.past = {}; rbState.pastLoading = {}; rbState.pastFirst = null;
  const res = await fetch('/api/benchmarking/rates').catch(() => null);
  rbState.data = res && res.ok ? await res.json() : { state: 'error' };
}

// Which view shows, the title pill, the subtitle and the mode bar
function applyBenchMode() {
  const real = rbState.canReal && (rbState.compSet || rbState.editing);
  document.getElementById('bench-real').hidden = !real;
  document.getElementById('bench-empty').hidden = real;
  document.getElementById('bench-sub-tags').textContent = 'BAR (published rates) · Occupancy (Kodo estimate)';

  const pill = document.getElementById('bench-mode-badge');
  const live = real && rbState.data && rbState.data.state === 'live';
  pill.hidden = !live;
  if (live) { pill.textContent = 'Live data available'; pill.className = 'pill--green bench-title-pill'; }

  const title = document.getElementById('bench-empty-title');
  const sub = document.getElementById('bench-empty-sub');
  const plans = document.getElementById('bench-empty-plans');
  const setup = document.getElementById('bench-empty-setup');
  if (!rbState.canReal) {
    title.textContent = 'Benchmark your hotel against a comp set';
    sub.textContent = 'Your BAR (published rates) and Kodo’s occupancy estimate, night by night, against up to 10 hotels you choose. Part of the Benchmarker and Advisory plans.';
    plans.hidden = false; setup.hidden = true;
  } else if (!real) {
    title.textContent = 'Choose your hotel and comp set';
    sub.textContent = 'Pick your hotel and 1 to 10 competitors. Kodo compares their BAR (published rates), collected every night, and the occupancy estimate for the next 30 nights.';
    plans.hidden = true; setup.hidden = false;
  }
  if (real) renderRateBenchmark();
}

document.getElementById('bench-empty-setup').addEventListener('click', () => rbOpenEditor());

// ── Render ──
function renderRateBenchmark() {
  const d = rbState.data;
  const cs = rbState.compSet;
  document.getElementById('rb-editor').hidden = !rbState.editing;

  const sub = cs && rbHotel(cs.subject_id);
  document.getElementById('rb-subject').innerHTML = sub
    ? `<div class="bench-prop-name">${fmt.esc(sub.name)}</div><div class="bench-prop-meta">${fmt.esc(sub.city)} · ${fmt.esc(sub.category)} · ${sub.keys} keys</div>`
    : '<div class="bench-prop-meta">No hotel chosen yet</div>';
  document.getElementById('rb-comps').innerHTML = cs
    ? cs.comp_ids.map(id => rbHotel(id)).filter(Boolean).map(h => `<span class="bench-comp-pill">${fmt.esc(h.name)}</span>`).join('')
    : '';

  const statusEl = document.getElementById('rb-status');
  const k = d && d.kpis;
  const updated = d && d.rates_updated ? KodoPeriod.day(d.rates_updated) : null;
  if (!d || !cs) statusEl.textContent = 'Choose your hotel and comp set to start.';
  else if (d.state === 'error') statusEl.textContent = 'The rate benchmark could not be loaded. Try again later.';
  else if (d.state === 'empty') statusEl.textContent = 'Not available yet. Rate tracking starts after the first full scrape.';
  else if (d.state === 'stale') statusEl.textContent = `Last live rates: ${updated} · not updated since · ${k.nights_with_rate} of ${d.window.nights} nights have live rates (prices up to 7 days old)`;
  else statusEl.textContent = `${k.nights_with_rate} of ${d.window.nights} nights have live rates · rates updated ${updated} · comp set of ${d.comps.length} hotel${d.comps.length === 1 ? '' : 's'}`;

  rbRenderKPIs();
  if (!rbState.rateCal) { const n = new Date(); rbState.rateCal = { y: n.getFullYear(), m: n.getMonth() + 1 }; }
  if (!rbState.occCal)  { const n = new Date(); rbState.occCal  = { y: n.getFullYear(), m: n.getMonth() + 1 }; }
  rbRenderCalendar('rate'); rbRenderCalendar('occ');
  rbRenderInsights();
}

function rbCard(id, value, sub) {
  const card = document.getElementById(id);
  const v = card.querySelector('.rb-kpi-val');
  const na = value == null;
  v.textContent = na ? 'Not available yet' : value;
  v.classList.toggle('kpi-value--na', na);
  card.querySelector('.rb-kpi-sub').textContent = sub || '';
  const d = rbState.data;
  const tip = KodoPeriod.tip({ source: 'published rates (scraped_rates.csv) and Kodo modelled occupancy' });
  KodoPeriod.set(card, { kind: 'next', days: 30 }, tip,
    { compare: d && d.rates_updated ? `rates updated ${KodoPeriod.day(d.rates_updated)}` : 'no rates collected yet' });
}

function rbRenderKPIs() {
  const d = rbState.data, k = d && d.kpis;
  const ok = k && d.state !== 'empty' && d.state !== 'error';
  rbCard('rbk-index', ok && k.rate_index != null ? String(Math.round(k.rate_index)) : null,
    ok && k.rate_index != null ? `Your published rate ÷ comp set median × 100 · ${k.nights_compared} nights compared` : '');
  rbCard('rbk-rate', ok && k.avg_rate != null ? rbMad(k.avg_rate) : null,
    ok && k.avg_rate != null ? `Comp set median ${rbMad(k.avg_comp_median)} · nights with your live rate` : '');
  rbCard('rbk-rank', ok && k.rank != null ? `${k.rank} of ${k.ranked_of}` : null,
    ok && k.rank != null ? 'By average published rate · 1 = highest' : '');
  rbCard('rbk-occ', ok && k.occ_subject != null ? `${k.occ_subject.toFixed(1)}%` : null,
    ok && k.occ_subject != null
      ? `${k.occ_subject_low != null && k.occ_subject_high != null ? `Range ${k.occ_subject_low}–${k.occ_subject_high}% · ` : ''}Comp set average ${k.occ_comp != null ? k.occ_comp.toFixed(1) + '%' : '–'} · Kodo estimate · modelled, not measured · Price coverage: ${rbConf(k.occ_confidence)} · model run ${k.model_run_date ? KodoPeriod.day(k.model_run_date) : '–'}`
      : '');
  rbCard('rbk-cover', ok ? `${k.nights_with_rate} of ${d.window.nights}` : null,
    ok ? 'Nights with a live published rate for your hotel' : '');
  const note = document.getElementById('rb-occ-note');
  note.textContent = ok
    ? `Kodo estimate · modelled, not measured · your hotel, with the comp set average below · Price coverage: ${rbConf(k.occ_confidence)} (how many recent prices we have, not accuracy) · model run ${k.model_run_date ? KodoPeriod.day(k.model_run_date) : '–'}`
    : 'Kodo estimate · modelled, not measured';
}

function rbRenderCalendar(type) {
  const cal = type === 'rate' ? rbState.rateCal : rbState.occCal;
  const { y, m } = cal;
  const MON = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  document.getElementById(`rb-${type}-month`).textContent = `${MON[m - 1]} ${y}`;
  const d = rbState.data;
  const byNight = {};
  (d && d.nights || []).forEach(n => { byNight[n.night] = n; });
  const first = (new Date(y, m - 1, 1).getDay() + 6) % 7, total = new Date(y, m, 0).getDate();
  const todayIso = localIsoDate(new Date()), monthKey = `${y}-${String(m).padStart(2, '0')}`;
  const hasPast = type === 'rate' && `${monthKey}-01` < todayIso;
  const past = hasPast ? rbState.past[monthKey] : null;
  if (hasPast && !past) rbLoadPast(monthKey);
  if (type === 'rate') {
    document.getElementById('rb-rate-note').textContent = hasPast
      ? 'Past nights: the last published rate seen before each night (yours, and below it the comp set median). BAR is the public price, not what guests paid. "No data": no price was collected for that night. Upcoming nights: your published rate and the comp set median.'
      : 'Each night: your published rate, and below it the comp set median. "–": no live price. Only the next 30 nights are tracked.';
  }
  let html = '<div class="bench-cal-dow-row">' + ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'].map(x => `<div class="bench-cal-dow">${x}</div>`).join('')
    + '</div><div class="bench-cal-days">' + '<div class="bench-cal-day bench-cal-empty"></div>'.repeat(first);
  for (let day = 1; day <= total; day++) {
    const iso = `${y}-${String(m).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    const n = byNight[iso];
    const wk = [0, 6].includes(new Date(y, m - 1, day).getDay()) ? ' bench-cal-weekend' : '';
    if (type === 'rate' && iso < todayIso) {           // past night: its last published rate
      const pn = past && past[iso];
      if (!past) { html += `<div class="bench-cal-day bench-cal-nodata${wk}"><span class="bench-cal-daynum">${day}</span></div>`; continue; }
      if (!pn || pn.subject_rate == null && pn.comp_median == null) {
        html += `<div class="bench-cal-day bench-cal-nodata rb-cal-past${wk}"${calTipAttrs(iso, [['No price collected before this night']])}><span class="bench-cal-daynum">${day}</span><span class="bench-cal-dayval rb-cal-nodata-txt">No data</span></div>`;
        continue;
      }
      const tip = [['Last published rate', rbMad(pn.subject_rate), pn.subject_source ? `${pn.subject_source}, collected ${KodoPeriod.day(pn.collected_on)}, ${pn.days_before} ${pn.days_before === 1 ? 'day' : 'days'} before` : 'No price collected for your hotel'],
                   ['Comp set median', rbMad(pn.comp_median), `last published rates of ${pn.comp_priced} hotel${pn.comp_priced === 1 ? '' : 's'}`]];
      if (pn.rate_index != null) tip.push(['Rate index', `${Math.round(pn.rate_index)}`]);
      html += `<div class="bench-cal-day rb-cal-past${wk}"${calTipAttrs(iso, tip)}>
        <span class="bench-cal-daynum">${day}</span>
        <span class="bench-cal-dayval">${pn.subject_rate != null ? rbShort(pn.subject_rate) : '–'}<span class="rb-cal-sub">${pn.comp_median != null ? 'med ' + rbShort(pn.comp_median) : 'med –'}</span></span></div>`;
      continue;
    }
    if (!n) { html += `<div class="bench-cal-day bench-cal-nodata rb-cal-out${wk}"${calTipAttrs(iso, [[iso < todayIso ? 'Past night: modelled occupancy covers upcoming nights only' : 'Outside the next 30 nights']])}><span class="bench-cal-daynum">${day}</span></div>`; continue; }
    let val, subTxt, sty, tip;
    if (type === 'rate') {
      val = rbShort(n.subject_rate); subTxt = n.comp_median != null ? `med ${rbShort(n.comp_median)}` : 'med –';
      sty = n.subject_rate != null ? adrCellStyle(n.subject_rate) : null;
      tip = [['Your published rate', rbMad(n.subject_rate), n.subject_source ? `${n.subject_source}, collected ${KodoPeriod.day(n.collected_on)}` : ''],
             ['Comp set median', rbMad(n.comp_median), `${n.comp_priced} hotel${n.comp_priced === 1 ? '' : 's'} with a rate`]];
      if (n.rate_index != null) tip.push(['Rate index', `${Math.round(n.rate_index)} · rank ${n.rank} of ${n.ranked_of}`]);
    } else {
      val = n.subject_occ != null ? `${Math.round(n.subject_occ)}%` : '–';
      subTxt = n.comp_occ != null ? `avg ${Math.round(n.comp_occ)}%` : 'avg –';
      sty = n.subject_occ != null ? occCellStyle(n.subject_occ / 100) : null;
      tip = [['Modelled occupancy', n.subject_occ != null ? occRange({ mid: n.subject_occ, low: n.subject_low, high: n.subject_high }) : '–', 'Kodo estimate']];
      if (n.subject_conf) tip.push(['Price coverage', COVERAGE_LABEL[rbConf(n.subject_conf)] || rbConf(n.subject_conf)]);
      tip.push(['Comp set average', n.comp_occ != null ? Math.round(n.comp_occ) + '%' : '–']);
    }
    const styAttr = sty ? `background:${sty.bg};color:${sty.col};${sty.fw ? `font-weight:${sty.fw};` : ''}${sty.border ? `border:${sty.border};` : ''}` : '';
    html += `<div class="bench-cal-day${sty ? '' : ' bench-cal-nodata'}${wk}" style="${styAttr}"${calTipAttrs(iso, tip)}>
      <span class="bench-cal-daynum" style="color:var(--text);opacity:1">${day}</span>
      <span class="bench-cal-dayval">${val}<span class="rb-cal-sub">${subTxt}</span></span></div>`;
  }
  document.getElementById(`rb-${type}-grid`).innerHTML = html + '</div>';
  KodoEvents.markCells(document.getElementById(`rb-${type}-grid`), (rbHotel(rbState.compSet && rbState.compSet.subject_id) || {}).city);
}

// Past months of the rate calendar: last published rates, loaded once a month
async function rbLoadPast(month) {
  if (rbState.pastLoading[month]) return;
  rbState.pastLoading[month] = true;
  try {
    const d = await (await fetch(`/api/benchmarking/rates/past?month=${month}`)).json();
    rbState.past[month] = Object.fromEntries((d.nights || []).map(n => [n.night, n]));
    if (d.first_month) rbState.pastFirst = d.first_month;
  } catch { rbState.past[month] = {}; }
  const cal = rbState.rateCal;
  if (`${cal.y}-${String(cal.m).padStart(2, '0')}` === month) rbRenderCalendar('rate');
}

// Calendar months: up to the one holding the 30th night; the rate calendar
// goes back to the first month with a price, occupancy starts this month
function rbStepMonth(type, step) {
  const cal = type === 'rate' ? rbState.rateCal : rbState.occCal;
  const now = new Date(), last = new Date(); last.setDate(last.getDate() + 30);
  let { y, m } = cal; m += step;
  if (m < 1) { m = 12; y--; } if (m > 12) { m = 1; y++; }
  const key = y * 12 + m, hi = last.getFullYear() * 12 + last.getMonth() + 1;
  let lo = now.getFullYear() * 12 + now.getMonth() + 1;
  if (type === 'rate') lo = rbState.pastFirst ? +rbState.pastFirst.slice(0, 4) * 12 + +rbState.pastFirst.slice(5) : lo - 24;
  if (key < lo || key > hi) return;
  cal.y = y; cal.m = m; rbRenderCalendar(type);
}
['rate', 'occ'].forEach(t => {
  document.getElementById(`rb-${t}-prev`).addEventListener('click', () => rbStepMonth(t, -1));
  document.getElementById(`rb-${t}-next`).addEventListener('click', () => rbStepMonth(t, 1));
});

// ── Insights (AI) ──
// The analyst is told this is the rate benchmark: published rates and
// modelled occupancy (Kodo estimate), never achieved figures.
function rbDataContext() {
  const d = rbState.data, k = d && d.kpis;
  if (!d || !k || d.state === 'empty' || d.state === 'error') return '';
  const pct = v => v != null ? v.toFixed(1) + '%' : 'n/a';
  return `RATE BENCHMARK MODE. These figures are BAR (PUBLISHED RATES: the nightly price shown for a one-night stay, 2 adults, no room count set, in MAD; collected every night) and OCCUPANCY (a Kodo estimate, modelled, not measured). They are not achieved figures: call them BAR or published rates and Kodo's occupancy estimate.
Hotel: ${d.subject.name} (${d.subject.city}, ${d.subject.category}). Comp set: ${d.comps.map(c => c.name).join(', ')}.
Next 30 nights (${d.window.start} to ${d.window.end}); rates last collected ${d.rates_updated}${d.state === 'stale' ? ' (not updated since)' : ''}.
Live published rate on ${k.nights_with_rate} of 30 nights for the hotel; ${k.nights_compared} nights also have a comp set median.
Average published rate MAD ${k.avg_rate ?? 'n/a'} vs comp set median MAD ${k.avg_comp_median ?? 'n/a'}; rate index ${k.rate_index ?? 'n/a'}; rank ${k.rank ?? 'n/a'} of ${k.ranked_of ?? 'n/a'} by average published rate.
Modelled occupancy ${pct(k.occ_subject)} vs comp set average ${pct(k.occ_comp)} (price coverage ${rbConf(k.occ_confidence) || 'n/a'}: how many recent prices exist, not accuracy; model run ${k.model_run_date || 'n/a'}).`;
}

const rbAiCache = new Map();
function rbRenderInsights(force = false) {
  const box = document.getElementById('rb-ai');
  const ctx = rbDataContext();
  if (!ctx) { box.innerHTML = '<p class="bench-loading">Not available yet. Insights need live published rates.</p>'; return; }
  const key = ctx;
  box.innerHTML = `<div class="bench-ai-summary${rbAiCache.has(key) && !force ? '' : ' bench-loading'}" id="rb-ai-summary">${rbAiCache.has(key) && !force ? rbAiCache.get(key) : 'Generating…'}</div>`;
  if (rbAiCache.has(key) && !force) return;
  fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages: [{ role: 'user', content: `Brief pricing commentary on this rate benchmark.\n${ctx}\n2-3 sentences. Cite specific numbers. Call them BAR (published rates) and Kodo's occupancy estimate.` }] }) })
    .then(r => r.json()).then(data => {
      if (rbDataContext() !== key) return;
      const el = document.getElementById('rb-ai-summary'); if (!el) return;
      el.className = 'bench-ai-summary';
      if (data.response) { const h = mdRender(data.response); rbAiCache.set(key, h); el.innerHTML = h; }
      else el.textContent = data.message || '';
    }).catch(() => { const el = document.getElementById('rb-ai-summary'); if (el) { el.className = 'bench-ai-summary'; el.textContent = ''; } });
}
document.getElementById('rb-ai-refresh').addEventListener('click', () => rbRenderInsights(true));

// ── Comp set editor ──
const rbNorm = s => String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
function rbOpenHotels() {
  return (hotels || []).filter(h => !h.status || /^(open|operating)$/i.test(h.status));
}
function rbSearch(q, exclude) {
  const n = rbNorm(q).trim();
  if (n.length < 2) return [];
  return rbOpenHotels().filter(h => !exclude.has(String(h.id)) && (rbNorm(h.name).includes(n) || rbNorm(h.city).includes(n))).slice(0, 8);
}
function rbResultHtml(h) {
  return `<button type="button" class="rb-result" data-id="${h.id}">${fmt.esc(h.name)}<span>${fmt.esc(h.city)} · ${fmt.esc(h.category)}</span></button>`;
}
function rbOpenEditor() {
  rbState.editing = true;
  rbState.draftSubject = rbState.compSet ? String(rbState.compSet.subject_id) : null;
  rbState.draftComps = rbState.compSet ? rbState.compSet.comp_ids.map(String) : [];
  document.getElementById('rb-msg').textContent = '';
  applyBenchMode();
  rbRenderEditor();
  document.getElementById('rb-editor').scrollIntoView({ block: 'nearest' });
}
function rbRenderEditor() {
  const s = rbState.draftSubject && rbHotel(rbState.draftSubject);
  document.getElementById('rb-subject-picked').textContent = s ? `${s.name} · ${s.city} · ${s.category}` : 'No hotel chosen yet';
  document.getElementById('rb-picked').innerHTML = rbState.draftComps.map(id => rbHotel(id)).filter(Boolean).map(h =>
    `<span class="bench-comp-pill">${fmt.esc(h.name)}<button type="button" class="bench-comp-pill-rm" data-rm="${h.id}" aria-label="Remove ${fmt.esc(h.name)}">×</button></span>`).join('')
    || '<span class="rb-msg">No comp set hotels yet</span>';
  document.getElementById('rb-save').disabled = !s || !rbState.draftComps.length;
}
async function rbSuggest() {
  if (!rbState.draftSubject) { document.getElementById('rb-msg').textContent = 'Choose your hotel first.'; return; }
  const r = await fetch(`/api/benchmarking/compset/suggest?subject_id=${encodeURIComponent(rbState.draftSubject)}`).then(x => x.json()).catch(() => ({}));
  const ids = (r.suggested || []).slice(0, 6);
  rbState.draftComps = ids;
  document.getElementById('rb-msg').textContent = ids.length ? `Suggested ${ids.length} hotels: same city, similar segment, nearest first.` : 'No similar hotels found in this city: add some by name.';
  rbRenderEditor();
}
document.getElementById('rb-edit').addEventListener('click', rbOpenEditor);
document.getElementById('rb-subject-q').addEventListener('input', e => {
  document.getElementById('rb-subject-results').innerHTML = rbSearch(e.target.value, new Set()).map(rbResultHtml).join('');
});
document.getElementById('rb-subject-results').addEventListener('click', e => {
  const b = e.target.closest('.rb-result'); if (!b) return;
  const changed = rbState.draftSubject !== b.dataset.id;
  rbState.draftSubject = b.dataset.id;
  rbState.draftComps = rbState.draftComps.filter(id => id !== b.dataset.id);
  document.getElementById('rb-subject-results').innerHTML = '';
  document.getElementById('rb-subject-q').value = '';
  rbRenderEditor();
  if (changed && !rbState.draftComps.length) rbSuggest();
});
document.getElementById('rb-comp-q').addEventListener('input', e => {
  const ex = new Set([...rbState.draftComps, rbState.draftSubject].filter(Boolean));
  document.getElementById('rb-comp-results').innerHTML = rbSearch(e.target.value, ex).map(rbResultHtml).join('');
});
document.getElementById('rb-comp-results').addEventListener('click', e => {
  const b = e.target.closest('.rb-result'); if (!b) return;
  if (rbState.draftComps.length >= 10) { document.getElementById('rb-msg').textContent = 'A comp set has at most 10 hotels.'; return; }
  rbState.draftComps.push(b.dataset.id);
  document.getElementById('rb-comp-results').innerHTML = '';
  document.getElementById('rb-comp-q').value = '';
  rbRenderEditor();
});
document.getElementById('rb-picked').addEventListener('click', e => {
  const b = e.target.closest('[data-rm]'); if (!b) return;
  rbState.draftComps = rbState.draftComps.filter(id => id !== b.dataset.rm);
  rbRenderEditor();
});
document.getElementById('rb-suggest').addEventListener('click', rbSuggest);
document.getElementById('rb-cancel').addEventListener('click', () => { rbState.editing = false; applyBenchMode(); });
document.getElementById('rb-save').addEventListener('click', async () => {
  const msg = document.getElementById('rb-msg');
  msg.textContent = 'Saving…';
  const r = await fetch('/api/benchmarking/compset', { method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ subject_id: rbState.draftSubject, comp_ids: rbState.draftComps }) }).catch(() => null);
  const data = r ? await r.json().catch(() => ({})) : {};
  if (!r || !r.ok) { msg.textContent = data.error || 'Could not save the comp set.'; return; }
  rbState.compSet = data.comp_set; rbState.editing = false;
  await loadRateBenchmark();
  applyBenchMode();
});

// ── Excel export (same labels and the methodology note) ──
function exportRateBenchmark() {
  if (!canExport()) { showUpgradeModal('Benchmarker & Advisory Only', 'Excel export is available on Benchmarker and Advisory plans.'); return; }
  const d = rbState.data;
  if (!d || !d.kpis) return;
  const k = d.kpis;
  const period = `Next 30 days · ${d.rates_updated ? 'rates updated ' + KodoPeriod.day(d.rates_updated) : 'no rates collected yet'}`;
  const na = v => v == null ? 'Not available yet' : v;
  const method = [...document.querySelectorAll('#bench-method .bench-method-body p')].map(p => ({ 'Methodology': p.textContent.trim() }));
  const kpis = [
    { 'Metric': 'Rate index', 'Your hotel': na(k.rate_index), 'Comp set': 100, 'Period': period, 'Note': 'Your published rate ÷ comp set median × 100' },
    { 'Metric': 'Average published rate (MAD)', 'Your hotel': na(k.avg_rate), 'Comp set': na(k.avg_comp_median), 'Period': period, 'Note': 'Comp set: median published rate. BAR (published rates), not what guests paid' },
    { 'Metric': 'Rate rank in comp set', 'Your hotel': k.rank != null ? `${k.rank} of ${k.ranked_of}` : 'Not available yet', 'Comp set': '', 'Period': period, 'Note': 'By average published rate, 1 = highest' },
    { 'Metric': 'Modelled occupancy % (Kodo estimate)', 'Your hotel': na(k.occ_subject), 'Comp set': na(k.occ_comp), 'Period': period, 'Note': `Modelled, not measured · price coverage ${rbConf(k.occ_confidence) || 'n/a'} (how many recent prices we have, not accuracy) · model run ${k.model_run_date || 'n/a'}` },
    { 'Metric': 'Rate coverage', 'Your hotel': `${k.nights_with_rate} of ${d.window.nights} nights`, 'Comp set': '', 'Period': period, 'Note': 'Nights with a live published rate for your hotel' },
  ];
  const nights = d.nights.map(n => ({
    'Night': n.night,
    'Your published rate (MAD)': n.subject_rate ?? '–',
    'Source': n.subject_source || '–',
    'Collected on': n.collected_on || '–',
    'Comp set median published rate (MAD)': n.comp_median ?? '–',
    'Comp set hotels with a rate': n.comp_priced,
    'Rate index': n.rate_index ?? '–',
    'Rank': n.rank != null ? `${n.rank} of ${n.ranked_of}` : '–',
    'Modelled occupancy % (Kodo estimate)': n.subject_occ ?? '–',
    'Modelled occupancy range %': n.subject_low != null && n.subject_high != null ? `${n.subject_low}–${n.subject_high}` : '–',
    'Comp set modelled occupancy %': n.comp_occ ?? '–',
    'Price coverage': rbConf(n.subject_conf) || '–',
  }));
  const comp = [d.subject, ...d.comps].map((h, i) => ({ 'Role': i ? 'Comp set' : 'Your hotel', 'Hotel': h.name, 'City': h.city, 'Segment': h.category, 'Keys': h.keys }));
  exportToExcel([
    { data: method, name: 'Methodology' },
    { data: kpis, name: 'KPI Summary' },
    { data: nights, name: 'Nightly Rates' },
    { data: comp, name: 'Comp Set' },
  ], `Kodo_Rate_Benchmark_${(d.subject.name || 'Hotel').replace(/[^a-zA-Z0-9]/g, '_')}_${new Date().toISOString().slice(0, 10)}`);
}
document.getElementById('btn-export-rb')?.addEventListener('click', exportRateBenchmark);

// ─── Global Search ────────────────────────────────────────────────

const searchIndex = { hotels: [], brands: [], cities: [], owners: [], pipeline: [], news: [] };
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
      searchText: `${h.name || ''} ${h.city || ''} ${h.brand_group || ''} ${h.owner || ''} ${h.owner_via || ''}`.toLowerCase(),
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

  if (ownersData) {
    searchIndex.owners = ownersData.map(o => ({
      id: o.id, name: o.name, via: o.via || '', hotels: o.total_hotels || 0,
      searchText: `${o.name || ''} ${o.full_name || ''} ${o.via || ''}`.toLowerCase(),
    }));
  } else if (!buildSearchIndex._owners) {
    // Owner profiles load with the Owners screen; fetch them once for search
    buildSearchIndex._owners = fetch('/api/owners').then(r => r.ok ? r.json() : null)
      .then(d => { if (d && !ownersData) { ownersData = d; buildSearchIndex(); } }).catch(() => {});
  }

  if (pipelineData) {
    searchIndex.pipeline = pipelineData.map(p => ({
      id: p.id,
      name: p.name || '',
      city: p.city || '',
      brand: p.brand || '',
      expected_opening: p.expected_opening || PIPE_NO_DATE,
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
    owners:   searchIndex.owners.filter(o => o.searchText.includes(q)).slice(0, 3),
    pipeline: searchIndex.pipeline.filter(p => p.searchText.includes(q)).slice(0, 3),
    news:     searchIndex.news.filter(a => a.searchText.includes(q)).slice(0, 2),
    tourism:  window.KodoOutlookSearch ? KodoOutlookSearch.match(q) : [],
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

  // Tourism outlook first: these queries are specific (a year, estimate, forecast, outlook)
  if (results.tourism.length) groups.push({
    label: 'Tourism',
    items: results.tourism.map(t => ({
      name: t.name,
      tagHtml: `<span class="tour-tag tour-tag--${t.kind}">${t.tag}</span>`,
      meta: t.meta,
      action() { closeSearch(); _srchSaveRecent(query); showTourismOutlook(t.year); },
    })),
  });

  if (results.hotels.length) groups.push({
    label: 'Hotels',
    items: results.hotels.map(h => ({
      name: h.name,
      meta: [h.city, h.category, h.keys ? h.keys.toLocaleString() + (h.keys === 1 ? ' key' : ' keys') : ''].filter(Boolean).join(' · '),
      metaHtml: fmt.esc(h.city) + ' · ' + getSegmentBadgeHtml(h.category) + (h.keys ? ' · ' + h.keys.toLocaleString() + (h.keys === 1 ? ' key' : ' keys') : ''),
      action() { closeSearch(); _srchSaveRecent(query); showHotelDetail(h.id); },
    })),
  });

  if (results.brands.length) groups.push({
    label: 'Brands',
    items: results.brands.map(b => ({
      name: b.brand,
      iconHtml: b.brand.startsWith('Independent') ? '' : brandLogoOrInitials(b.brand, 26),
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
        selectCity(c.city);
      },
    })),
  });

  if (results.owners.length) groups.push({
    label: 'Owners',
    items: results.owners.map(o => ({
      name: o.name,
      iconHtml: getOwnerLogoImg(o.name, 26),
      meta: [o.via ? `via ${o.via}` : '', `${o.hotels} ${o.hotels === 1 ? 'hotel' : 'hotels'}`].filter(Boolean).join(' · '),
      action() { closeSearch(); _srchSaveRecent(query); _srchNavigateToScreen('owners'); showOwnerDetail(o.id); },
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
    container.innerHTML = getEmptyStateHtml(`No results for "${fmt.esc(query)}"`);
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
      const text = `<div class="search-result-name">${fmt.esc(item.name)}${item.tagHtml ? ' ' + item.tagHtml : ''}</div><div class="search-result-meta">${item.metaHtml || fmt.esc(item.meta)}</div>`;
      el.innerHTML = item.iconHtml ? `<div class="search-result-row"><span class="search-result-logo">${item.iconHtml}</span><div>${text}</div></div>` : text;
      el.addEventListener('click', item.action);
      groupEl.appendChild(el);
    });
    container.appendChild(groupEl);
  });
}

// Search event wiring. main.js loads before the search modal's markup in
// index.html, so the listeners are attached once the page is parsed.
function initSearchEvents() {
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
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initSearchEvents);
else initSearchEvents();

// ─── Boot ─────────────────────────────────────────────────────────

async function boot() {
  let profiles;
  [apiData, hotels, profiles] = await Promise.all([
    fetch('/api/data').then(r => r.json()),
    fetch('/api/hotels').then(r => r.json()),
    fetch('/api/brand-profiles').then(r => r.ok ? r.json() : {}).catch(() => ({})),
  ]);
  // Descriptions kept in the data (brand_profiles.json) fill the brands the code has none for
  Object.entries(profiles || {}).forEach(([bg, p]) => { if (p.description && !BRAND_DESCRIPTIONS[bg]) BRAND_DESCRIPTIONS[bg] = p.description; });
  KodoBar.setMeta(apiData && apiData.bar);
  readDashUrl();                 // ?dest=…&tab=… (old /dashboard links: All Morocco)
  writeDashUrl();                // an old ?tab=seasonality now reads ?tab=overview
  setDestMetric(state.destMetric);
  buildCityPills();
  buildSegPills();
  buildOwnerSelect();
  render();
  buildSearchIndex();
  // /dashboard#hotel=ID opens that hotel's profile (links from the admin's Data health page)
  const deep = location.hash.match(/^#hotel=(\d+)$/);
  if (deep && hotels.some(h => +h.id === +deep[1])) showHotelDetail(+deep[1]);
}

// Hotels screen owner filter: every owner in the hotel list (most hotels
// first), Undisclosed last; the label carries the "via" company
function buildOwnerSelect() {
  const sel = document.getElementById('hotels-owner-select');
  if (!sel) return;
  const counts = {}, via = {};
  hotels.forEach(h => { if (h.owner) { counts[h.owner] = (counts[h.owner] || 0) + 1; if (h.owner_via) via[h.owner] = h.owner_via; } });
  const names = Object.keys(counts).filter(o => o !== 'Undisclosed')
    .sort((a, b) => counts[b] - counts[a] || a.localeCompare(b));
  if (counts.Undisclosed) names.push('Undisclosed');
  const keep = names.includes(sel.value) ? sel.value : 'all';
  sel.replaceChildren(new Option('All owners', 'all'),
    ...names.map(o => new Option(via[o] ? `${o} (via ${via[o]})` : o, o)));
  sel.value = keep;
  if (keep === 'all' && hotelsState.owner !== 'all') hotelsState.owner = 'all';
}

// Fetch current user info and populate tier badge
fetch('/api/me').then(r => r.ok ? r.json() : null).then(me => {
  if (!me) return;
  const badge = document.getElementById('tier-badge');
  if (!badge) return;
  // Colour comes from data-plan (tokens.css); an unknown or missing plan shows as Observer
  const PLAN_LABELS = { observer: 'Observer', benchmarker: 'Benchmarker', advisory: 'Advisory' };
  const plan = PLAN_LABELS[me.tier] ? me.tier : 'observer';
  badge.textContent = PLAN_LABELS[plan];
  badge.className = `tier-badge tier-badge--${plan} pill--plan`;
  badge.dataset.plan = plan;
  badge.style.display = '';
  window._kodoUser = me;
  // Hide export buttons and dropdowns for Observer tier
  if (me.tier === 'observer') {
    document.querySelectorAll(
      '.export-btn, #tourism-export-year'
    ).forEach(el => { el.style.display = 'none'; });
  }
});

// ── Reports ──────────────────────────────────────────────────────────────────
// Real data model: /api/reports/available returns a fixed set of cities
// (7 regions + "Morocco" national) and periods (currently "Q3 2026",
// "Q4 2026", "Annual 2026") — there is no "report type" beyond city-level
// market reports, no stored description/date, and no pre-existing file;
// each city+period combination is generated on demand by POSTing to
// /api/reports/generate, which returns a fresh PDF (server-cached 24h).
// Flattened here into one row per city×period so the Period filter has
// something real to filter by.
let reportsInited = false;
let reportsAllRows = [];
let reportsFilterState = { type: 'all', period: 'all', search: '' };

async function initReports() {
  if (reportsInited) return;
  const listEl = document.getElementById('reports-grid');
  if (!listEl) return;

  try {
    const res = await fetch('/api/reports/available');
    if (!res.ok) return;
    const data = await res.json();

    // Only the periods real data covers (report_periods() on the server):
    // the first is "Q4 2026 (partial)", from 3 November 2026
    const periods = data.periods || [];
    const cities  = data.cities  || [];

    reportsAllRows = [];
    periods.forEach(period => {
      cities.forEach(cityMeta => {
        reportsAllRows.push({
          city:   cityMeta.city,
          hotels: cityMeta.hotels,
          keys:   cityMeta.keys,
          period: period.id,
          periodLabel: period.label,
          since:  period.since,
          partial: period.partial,
          type:   cityMeta.city === 'Morocco' ? 'Market' : 'City',
        });
      });
    });

    buildReportFilters(periods);
    wireReportSearch();
    renderReportList();

    reportsInited = true;
  } catch (e) {
    console.error('initReports error:', e);
  }
}

function buildReportFilters(periods) {
  const typeEl   = document.getElementById('report-type-filters');
  const periodEl = document.getElementById('report-period-filters');
  if (!typeEl || !periodEl) return;

  // Type: the city reports and the Morocco market report
  const typeOptions = ['All', 'City', 'Market'];
  typeEl.innerHTML = typeOptions.map((t, i) =>
    `<button class="list-pill${i === 0 ? ' active' : ''}" data-filter="type" data-value="${i === 0 ? 'all' : fmt.esc(t)}">${fmt.esc(t)}</button>`
  ).join('');

  const periodOptions = [{ id: 'all', label: 'All' }, ...periods];
  periodEl.innerHTML = periodOptions.map((p, i) =>
    `<button class="list-pill${i === 0 ? ' active' : ''}" data-filter="period" data-value="${fmt.esc(p.id)}">${fmt.esc(p.label)}</button>`
  ).join('');

  [typeEl, periodEl].forEach(container => {
    container.addEventListener('click', e => {
      const btn = e.target.closest('.list-pill');
      if (!btn) return;
      container.querySelectorAll('.list-pill').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      reportsFilterState[btn.dataset.filter] = btn.dataset.value;
      renderReportList();
    });
  });
}

function wireReportSearch() {
  const input = document.getElementById('report-search');
  if (!input) return;
  input.addEventListener('input', () => {
    reportsFilterState.search = input.value.trim().toLowerCase();
    renderReportList();
  });
}

function resetReportFilters() {
  reportsFilterState = { type: 'all', period: 'all', search: '' };
  const searchInput = document.getElementById('report-search');
  if (searchInput) searchInput.value = '';
  document.querySelectorAll('#report-type-filters .list-pill, #report-period-filters .list-pill')
    .forEach(b => b.classList.toggle('active', b.dataset.value === 'all'));
  renderReportList();
}

// Re-renders just the row list from reportsAllRows + the current filter
// state — called on every filter-pill click and search keystroke, and
// re-attaches each row's action handler since the list is rebuilt from
// scratch each time (no stale DOM nodes to assume still exist).
function renderReportList() {
  const listEl  = document.getElementById('reports-grid');
  const countEl = document.getElementById('report-count');
  if (!listEl) return;

  const { type, period, search } = reportsFilterState;
  const filtered = reportsAllRows.filter(r => {
    if (type !== 'all' && r.type !== type) return false;
    if (period !== 'all' && r.period !== period) return false;
    if (search && !r.city.toLowerCase().includes(search)) return false;
    return true;
  });

  if (countEl) countEl.textContent = `${filtered.length} report${filtered.length !== 1 ? 's' : ''}`;

  if (!reportsAllRows.length) {
    listEl.innerHTML = KodoBar.collecting('The first report period opens once published rates have been collected.');
    return;
  }
  if (!filtered.length) {
    listEl.innerHTML = `<p class="list-empty">No reports match your filters.<button class="list-clear-btn" id="report-clear-filters">Clear filters</button></p>`;
    document.getElementById('report-clear-filters')?.addEventListener('click', resetReportFilters);
    return;
  }

  const tier = (window._kodoUser && window._kodoUser.tier) || '';
  const canGenerate = tier === 'benchmarker' || tier === 'advisory';

  listEl.innerHTML = filtered.map(r => `
    <div class="report-row">
      <div class="report-main">
        <span class="report-title">${fmt.esc(r.city)}</span>
        <span class="report-desc">${r.hotels} hotels tracked · ${r.keys != null ? r.keys.toLocaleString('en') : '—'} keys${r.partial ? ` · ${KodoBar.since()}` : ''}</span>
      </div>
      <span class="report-type">${fmt.esc(r.type)}</span>
      <span class="report-date">${fmt.esc(r.periodLabel)}</span>
      <button class="report-action" data-city="${fmt.esc(r.city)}" data-period="${fmt.esc(r.period)}">Generate Report</button>
    </div>`).join('');

  listEl.querySelectorAll('.report-action').forEach(btn => {
    btn.addEventListener('click', () => handleReportGenerate(btn, canGenerate));
  });
}

// Same generate-and-download flow the old per-city cards used (POST
// city+period to /api/reports/generate, download the returned PDF blob),
// just reattached to a flat row's button instead of a card, with a
// transient status line appended under the row instead of a fixed slot.
async function handleReportGenerate(btn, canGenerate) {
  if (!canGenerate) {
    showUpgradeModal('Benchmarker & Advisory Only', 'Reports are available on Benchmarker and Advisory plans. Upgrade to download institutional-grade PDF market reports.');
    return;
  }

  const city   = btn.dataset.city;
  const period = btn.dataset.period;
  const theme  = 'light'; // Reports are light-mode only.
  const row    = btn.closest('.report-row');

  let statusEl = row.querySelector('.report-row-status');
  if (!statusEl) {
    statusEl = document.createElement('div');
    statusEl.className = 'report-row-status';
    row.appendChild(statusEl);
  }

  btn.disabled = true;
  btn.textContent = 'Generating…';
  statusEl.classList.remove('is-error');
  statusEl.textContent = 'Generating your report — this may take 30–60 seconds.';

  try {
    const r = await fetch('/api/reports/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ city, period, theme }),
    });

    if (!r.ok) {
      const err = await r.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(err.error || 'Generation failed');
    }

    const blob  = await r.blob();
    const url   = URL.createObjectURL(blob);
    const a     = document.createElement('a');
    const safe  = city.replace(/ \/ /g, '-').replace(/ /g, '-');
    const safep = period.replace(/ /g, '-');
    a.href     = url;
    a.download = `Kodo_${safe}_${safep}_${theme}.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    statusEl.textContent = 'Report ready — downloading now.';
  } catch (err) {
    statusEl.textContent = `Error: ${err.message}`;
    statusEl.classList.add('is-error');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Generate Report';
  }
}

// ─── Excel Export ─────────────────────────────────────────────────────────────

function canExport() {
  const tier = (window._kodoUser && window._kodoUser.tier) || '';
  return tier === 'benchmarker' || tier === 'advisory';
}

// Spreadsheet colours: light-mode values of static/css/tokens.css (Excel has
// no dark mode). Category cells get the family tint with its text colour.
const XLSX_COLORS = {
  headerFill: 'F4F4F2', headerText: '1F1E1C', headerRule: '0075DE', text: '1F1E1C',
  families: {
    blue:   { text: '006DD0', tint: 'E6F3FE' },
    green:  { text: '127F48', tint: 'E4F8EC' },
    orange: { text: 'BB4A0E', tint: 'FFEEE6' },
    violet: { text: '5B3FC4', tint: 'EEE9FD' },
    sky:    { text: '0976A6', tint: 'E3F6FF' },
    grey:   { text: '5F5B55', tint: 'F1F0EE' },
    red:    { text: 'C4332F', tint: 'FDECEC' },
  },
};

// Column name -> function(value) returning a colour family, or null
const XLSX_CATEGORY_COLUMNS = {
  'Segment':      v => SEGMENT_FAMILY[v] || null,
  'Category':     v => SEGMENT_FAMILY[v] || null,
  'Status':       v => v === 'Under Construction' ? 'blue' : (v ? 'grey' : null),
  'Data Quality': v => {
    const q = String(v || '').toLowerCase();
    if (!q) return null;
    if (q.startsWith('verified')) return 'green';
    return q.includes('uncertain') ? 'orange' : 'grey';
  },
};

function styleSheet(ws, data) {
  if (!ws['!ref']) return;
  const keys  = Object.keys(data[0] || {});
  const range = XLSX.utils.decode_range(ws['!ref']);
  for (let c = range.s.c; c <= range.e.c; c++) {
    const head = ws[XLSX.utils.encode_cell({ r: 0, c })];
    if (head) head.s = {
      font:   { bold: true, color: { rgb: XLSX_COLORS.headerText } },
      fill:   { patternType: 'solid', fgColor: { rgb: XLSX_COLORS.headerFill } },
      border: { bottom: { style: 'thin', color: { rgb: XLSX_COLORS.headerRule } } },
    };
    const familyOf = XLSX_CATEGORY_COLUMNS[keys[c]];
    if (!familyOf) continue;
    for (let r = 1; r <= range.e.r; r++) {
      const cell = ws[XLSX.utils.encode_cell({ r, c })];
      const fam  = cell && XLSX_COLORS.families[familyOf(cell.v)];
      if (!fam) continue;
      cell.s = {
        font: { bold: true, color: { rgb: fam.text } },
        fill: { patternType: 'solid', fgColor: { rgb: fam.tint } },
      };
    }
  }
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
    styleSheet(ws, data);
    XLSX.utils.book_append_sheet(wb, ws, name);
  });
  const about = [{
    'Source':    'Kodo Hospitality — Morocco Hotel Market Intelligence',
    'Website':   'kodohospitality.com',
    'Generated': new Date().toLocaleDateString('en-GB'),
    'Note':      'Kodo proprietary estimates unless marked Verified',
    'Contact':   'advisory@kodohospitality.com',
  }];
  const wsAbout = XLSX.utils.json_to_sheet(about);
  wsAbout['!cols'] = Object.keys(about[0]).map(k => ({
    wch: Math.max(k.length, ...about.map(r => String(r[k] ?? '').length))
  }));
  styleSheet(wsAbout, about);
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
  const asOf = KodoPeriod.label(KodoPeriod.today());
  const data = filtered.map(h => ({
    'Hotel Name':       h.name || 'N/A',
    'City':             h.city || 'N/A',
    'Segment':          h.category || 'N/A',
    'Brand Group':      h.brand_group || 'N/A',
    'Keys':             h.keys ?? 'N/A',
    'BAR (MAD)':        h.bar_mad ?? 'Not enough prices yet',
    'BAR nights':       h.bar_nights || 0,
    'BAR period':       KodoBar.caption(),
    'Occupancy % (Kodo estimate)': h.occupancy != null ? (h.occupancy * 100).toFixed(1) + '%' : 'N/A',
    'Rooms RevPAR (MAD, est.)': h.revpar_mad ?? 'N/A',
    'Estimate period':  'Next 30 nights',
    'Keys As Of':       asOf,
    'Year Established': h.year_opened_verified === 'verified' && h.year_opened != null ? h.year_opened : 'N/A',
    'Owner':            h.owner || 'Undisclosed',
    'Owner via':        h.owner_via || '',
    'Data Quality':     h.data_quality || 'Estimated',
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
  const asOf = KodoPeriod.label(KodoPeriod.today());
  const data = filteredPipeline().map(p => ({
    'Project Name':       p.name,
    'City':               p.city,
    'Category':           p.category,
    'Brand':              p.brand,
    'Brand Group':        p.brand_group,
    'Keys':               p.keys || 'TBC',
    'New Keys':           p.conversion ? 0 : (p.keys || 'TBC'),
    'Converts Hotel':     p.conversion ? (p.converts_hotel_name || p.converts_hotel_id) : '',
    'Expected Opening':   p.expected_opening ?? PIPE_NO_DATE,
    'Status':             p.status,
    'Investment (MAD M)': p.investment_mad ? Math.round(p.investment_mad / 1e6) : 'N/A',
    'Data As Of':         asOf,
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
  const asOf = KodoPeriod.label(KodoPeriod.today());
  const data = filteredBrands().map((b, i) => ({
    'Rank':              i + 1,
    'Brand Group':       b.brand_group,
    'Hotels':            b.hotels,
    'Total Keys':        b.total_keys,
    'Market Share %':    b.market_share_keys_pct != null ? b.market_share_keys_pct.toFixed(1) + '%' : 'N/A',
    'BAR (MAD)':         b.bar_mad == null ? 'Not enough prices yet' : b.bar_limited ? 'Limited data' : b.bar_mad,
    'BAR hotels':        b.bar_hotels || 0,
    'BAR period':        KodoBar.caption(),
    'Occupancy % (Kodo estimate)': b.avg_occupancy != null ? (b.avg_occupancy * 100).toFixed(1) + '%' : 'N/A',
    'Rooms RevPAR (MAD, est.)': b.avg_revpar != null ? Math.round(b.avg_revpar) : b.revpar_limited ? KodoBar.LIMITED : 'N/A',
    'Estimate period':   'Next 30 nights',
    'Keys As Of':        asOf,
    'Cities Present':    Array.isArray(b.cities) ? b.cities.join(', ') : 'N/A',
    'Pipeline Projects': b.pipeline_projects || 0,
    'Pipeline Keys':     b.pipeline_keys || 0,
  }));
  exportToExcel([{ data, name: 'Brands' }], `Kodo_Brands_${date}`);
}

function exportTourism() {
  if (!canExport()) {
    showUpgradeModal('Benchmarker & Advisory Only', 'Excel export is available on Benchmarker and Advisory plans. Upgrade to download tourism intelligence data.');
    return;
  }
  if (!tourismData) { loadTourismData().then(exportTourism).catch(() => {}); return; }
  const rowsOf = metric => tourBy(metric).flatMap(s => s.points.map(p => ({
    Series: s.label, Period: p.period, Value: p.value, Unit: s.unit, Status: p.status + (p.covid ? ' · COVID year' : ''),
  })));
  const F = tourismData.forecast, E26 = F.estimate_2026 || {};
  const fc = [];
  const add = (what, unit, f) => fc.push({ Item: what, Unit: unit, Base: f.base, Low: f.low, High: f.high, Label: 'Kodo forecast (2027F), not official' });
  const est = (what, unit, v) => v != null && fc.push({ Item: what, Unit: unit, Base: v, Low: '', High: '', Label: 'Kodo estimate (2026E), not official' });
  const UNITS = { arrivals: 'arrivals', nights: 'nights', occupancy: '%', receipts: 'MAD million', air_passengers: 'passengers' };
  Object.entries(F.nowcast_2026).forEach(([k, f]) => est(`${k} 2026E`, UNITS[k] || '', f.base));
  Object.entries(E26.markets || {}).forEach(([k, v]) => est(`Arrivals from ${k} 2026E`, 'arrivals', v));
  Object.entries(E26.cities_occupancy || {}).forEach(([k, v]) => est(`Occupancy ${k} 2026E`, '%', v));
  Object.entries(E26.airports || {}).forEach(([k, v]) => est(`Passengers ${k} 2026E`, 'passengers', v));
  (E26.receipts_monthly || []).forEach(m => est(`Receipts ${m.month} (2026E)`, 'MAD million', m.value));
  Object.entries(F.forecast_2027).forEach(([k, f]) => add(`${k} 2027F`, f.unit || UNITS[k] || '', f));
  Object.entries(F.markets_2027).forEach(([k, f]) => add(`Arrivals from ${k} 2027F`, 'arrivals', f));
  Object.entries(F.cities_occupancy_2027).forEach(([k, f]) => add(`Occupancy ${k} 2027F`, '%', f));
  Object.entries(F.airports_2027).forEach(([k, f]) => add(`Passengers ${k} 2027F`, 'passengers', f));
  (F.forecast_2027.receipts?.monthly || []).forEach(m => add(`Receipts ${m.month} (2027F)`, 'MAD million', m));
  const notes = [...tourismData.notes, 'Source: official Moroccan statistics and Kodo analysis. See kodohospitality.com/methodology.'];
  // The year selected at the top of the page, first, with the same labels as the page
  const key = tourKey(document.getElementById('tourism-export-year')?.value);
  const cur = tourYearFigures(key), kodo = TOUR_KODO[key];
  const status = kodo ? kodo.note : 'Official';
  const yr = [];
  const put = (item, unit, f) => yr.push({ Year: cur.label, Item: item, Unit: unit,
    Value: f == null || f.base == null ? TOUR_NOT : f.base, Low: f && f.low != null ? f.low : '', High: f && f.high != null ? f.high : '', Status: status });
  put('Arrivals (MRE included)', 'arrivals', cur.arrivals);
  put('Nights, classified accommodation', 'nights', cur.nights);
  put('Travel receipts', 'MAD million', cur.receipts);
  put('Occupancy, classified accommodation', '%', cur.occ);
  put('Airport passengers', 'passengers', cur.air);
  const rng = (grp, k) => cur.ranges && cur.ranges[grp] ? cur.ranges[grp][k] : null;
  Object.entries(cur.markets).sort((a, b) => b[1] - a[1]).forEach(([k, v]) => put(`Arrivals from ${k}`, 'arrivals', rng('markets', k) || { base: v }));
  cur.notMarkets.forEach(k => put(`Arrivals from ${k}`, 'arrivals', null));
  Object.entries(cur.regions).sort((a, b) => b[1] - a[1]).forEach(([k, v]) => put(`Nights, ${k}`, 'nights', rng('regions', k) || { base: v }));
  Object.entries(cur.cities).forEach(([k, v]) => put(`Occupancy, ${k}`, '%', rng('cities', k) || { base: v }));
  cur.notCities.forEach(k => put(`Occupancy, ${k}`, '%', null));
  Object.entries(cur.airports).forEach(([k, v]) => put(`Passengers, ${k}`, 'passengers', rng('airports', k) || { base: v }));
  if (kodo) ((tourismData.forecast.not_forecast || {}).items || []).forEach(k => put(k[0].toUpperCase() + k.slice(1), '', null));
  exportToExcel(
    [
      { data: yr, name: `Year ${cur.label}` },
      { data: [...rowsOf('arrivals'), ...rowsOf('arrivals_by_mode'), ...rowsOf('arrivals_by_entry')], name: 'Arrivals' },
      { data: rowsOf('arrivals_by_market'), name: 'Arrivals by market' },
      { data: [...rowsOf('nights'), ...rowsOf('nights_by_region'), ...rowsOf('nights_by_market')], name: 'Nights' },
      { data: rowsOf('occupancy'), name: 'Occupancy' },
      { data: [...rowsOf('receipts'), ...rowsOf('receipts_by_country')], name: 'Receipts' },
      { data: [...rowsOf('air_passengers'), ...rowsOf('airport_passengers')], name: 'Airports' },
      { data: fc, name: 'Kodo 2026E and 2027F' },
      { data: notes.map(n => ({ Note: n })), name: 'Notes' },
    ],
    `Kodo_Tourism_Morocco_${cur.label}`
  );
}

// ─── Owners screen ───────────────────────────────────────────────────────────

var ownersData = null;
var ownerDetailData = null;
var ownerPortfolioSort = { col: null, dir: 1 };

async function initOwners() {
  if (ownersData) { renderOwnerCards(); return; }
  showLoading(document.getElementById('owners-grid'));
  try {
    const res = await fetch('/api/owners');
    ownersData = await res.json();
    renderOwnerCards();
  } catch(e) {
    document.getElementById('owners-grid').innerHTML = '<p style="color:var(--text-muted);font-size:12px">Error loading owners.</p>';
  }
}

function renderOwnerCards() {
  var owners = ownersData || [];
  // KPI row
  var totalKeys = owners.reduce(function(s, o) { return s + (o.total_keys || 0); }, 0);
  document.getElementById('okpi-count').textContent = owners.length;
  document.getElementById('okpi-keys').textContent = totalKeys.toLocaleString();
  const ownerTip = KodoPeriod.tip({ source: 'Kodo owner profiles, keys from the Kodo hotel database', note: 'count when this page loaded' });
  ['okpi-count', 'okpi-keys'].forEach(id => KodoPeriod.set(document.getElementById(id).closest('.kpi-card'), KodoPeriod.today(), ownerTip));

  // Hide detail, show grid
  document.getElementById('screen-owner-detail').style.display = 'none';
  document.getElementById('owners-kpi-row').style.display = '';
  document.getElementById('owners-grid').style.display = '';

  var grid = document.getElementById('owners-grid');
  if (!owners.length) {
    grid.innerHTML = '<p style="color:var(--text-muted);font-size:12px">No owners tracked yet.</p>';
    return;
  }

  grid.innerHTML = owners.map(function(o) {
    var cities = (o.cities || []).slice(0, 3).join(', ') + ((o.cities || []).length > 3 ? ' +' + ((o.cities || []).length - 3) + ' more' : '');
    var brands = (o.brands_operated || []).slice(0, 3).join(', ') + ((o.brands_operated || []).length > 3 ? ' +' + ((o.brands_operated || []).length - 3) + ' more' : '');
    return '<div class="owner-card" onclick="showOwnerDetail(\'' + fmt.esc(o.id) + '\')">' +
      '<div style="display:flex;align-items:center;justify-content:space-between">' +
        '<div style="display:flex;align-items:center">' +
          getOwnerLogoImg(o.name, 40) +
          '<div>' +
            '<div style="font-family:\'Sweet Sans Pro\',sans-serif;font-size:13px;font-weight:400;text-transform:uppercase;letter-spacing:0.04em;color:var(--text)">' + fmt.esc(o.name) + '</div>' +
            (o.via ? '<div style="font-family:\'Sweet Sans Pro\',sans-serif;font-size:10px;color:var(--text-muted);margin-top:2px">via ' + fmt.esc(o.via) + '</div>' : '') +
          '</div>' +
        '</div>' +
        ownerTypeBadge(o.type || 'Private') +
      '</div>' +
      '<div class="owner-stats-row">' +
        '<div class="owner-stat-item"><span class="owner-stat-label">Hotels</span><span class="owner-stat-value">' + (o.total_hotels || 0) +
          (o.pipeline_hotels ? '<span class="owner-stat-pipe" title="' + o.pipeline_hotels + ' not open yet (pipeline), ' + (o.pipeline_keys || 0).toLocaleString() + ' keys">+' + o.pipeline_hotels + ' pipeline</span>' : '') + '</span></div>' +
        '<div class="owner-stat-item"><span class="owner-stat-label">Keys</span><span class="owner-stat-value">' + (o.total_keys || 0).toLocaleString() + '</span></div>' +
        '<div class="owner-stat-item"><span class="owner-stat-label">Cities</span><span class="owner-stat-value">' + (o.cities || []).length + '</span></div>' +
        '<div class="owner-stat-item"><span class="owner-stat-label">Operators</span><span class="owner-stat-value">' + (o.brands_operated || []).length + '</span></div>' +
      '</div>' +
      '<div style="font-family:\'Sweet Sans Pro\',sans-serif;font-size:10px;color:var(--text-muted)">' +
        (cities ? '<span style="color:var(--text-faint)">Cities: </span>' + fmt.esc(cities) : '') +
      '</div>' +
    '</div>';
  }).join('');
}

async function showOwnerDetail(ownerId) {
  document.getElementById('owners-kpi-row').style.display = 'none';
  document.getElementById('owners-grid').style.display = 'none';
  var detail = document.getElementById('screen-owner-detail');
  detail.style.display = '';
  scrollMainToTop();
  showLoading(document.getElementById('owner-detail-header'));

  try {
    const res = await fetch('/api/owners/' + ownerId);
    ownerDetailData = await res.json();
    renderOwnerDetail(ownerDetailData);
  } catch(e) {
    document.getElementById('owner-detail-header').innerHTML = '<p style="color:var(--text-muted)">Error loading owner.</p>';
  }
}

function renderOwnerDetail(o) {
  // Header
  document.getElementById('owner-detail-header').innerHTML =
    '<div style="display:flex;align-items:center;gap:12px;margin-bottom:14px">' +
      getOwnerLogoImg(o.name, 52) +
      '<div>' +
        '<h1 style="font-family:\'Sweet Sans Pro\',sans-serif;font-size:20px;font-weight:400;text-transform:uppercase;letter-spacing:0.06em;color:var(--text);margin:0">' + fmt.esc(o.name) + '</h1>' +
        (o.via ? '<div style="font-family:\'Sweet Sans Pro\',sans-serif;font-size:12px;color:var(--text-muted);margin-top:4px">via ' + fmt.esc(o.via) + '</div>' : '') +
        '<div style="display:flex;align-items:center;gap:8px;margin-top:6px">' +
          ownerTypeBadge(o.type || 'Private') +
        '</div>' +
      '</div>' +
    '</div>';

  // About card
  if (o.description) {
    document.getElementById('owner-about-slot').innerHTML =
      '<div class="brand-about-card" style="margin-bottom:20px">' +
        '<p style="font-family:\'Sweet Sans Pro\',sans-serif;font-size:13px;color:var(--text-muted);line-height:1.65;margin:0">' + fmt.esc(o.description) + '</p>' +
      '</div>';
  } else {
    document.getElementById('owner-about-slot').innerHTML = '';
  }

  // KPI row
  document.getElementById('odkpi-hotels').textContent = o.total_hotels || 0;
  // A project not open yet (pipeline) is listed, but not in these totals
  const kpiCard = document.getElementById('odkpi-hotels').closest('.kpi-card');
  kpiCard.querySelector('.owner-kpi-pipe')?.remove();
  if (o.pipeline_hotels) {
    const note = document.createElement('span');
    note.className = 'kpi-meta owner-kpi-pipe';
    note.textContent = `+ ${o.pipeline_hotels} in the pipeline (${(o.pipeline_keys || 0).toLocaleString()} keys)`;
    kpiCard.appendChild(note);
  }
  document.getElementById('odkpi-keys').textContent = (o.total_keys || 0).toLocaleString();
  document.getElementById('odkpi-cities').textContent = (o.cities || []).length;
  document.getElementById('odkpi-brands').textContent = (o.brands_operated || []).length;
  const ownerTip = KodoPeriod.tip({ source: 'Kodo owner profile, keys from the Kodo hotel database', note: 'count when this page loaded' });
  ['odkpi-hotels', 'odkpi-keys', 'odkpi-cities', 'odkpi-brands'].forEach(id =>
    KodoPeriod.set(document.getElementById(id).closest('.kpi-card'), KodoPeriod.today(), ownerTip));
  // Live figures over the owner's open hotels (not its pipeline projects)
  const ownHotels = (o.hotels || []).filter(x => x.hotel_id && !x.pipeline)
    .map(x => (hotels || []).find(h => +h.id === +x.hotel_id)).filter(Boolean);
  KodoLive.cards({ rate: 'odkpi-rate', occ: 'odkpi-occ', revpar: 'odkpi-revpar' }, ownHotels);

  // Destination pills
  document.getElementById('owner-destinations-row').innerHTML =
    '<span style="font-family:\'Sweet Sans Pro\',sans-serif;font-size:9px;text-transform:uppercase;letter-spacing:0.08em;color:var(--text-faint);margin-right:8px">Cities</span>' +
    (o.cities || []).map(function(c) {
      return '<span class="brand-meta-pill">' + fmt.esc(c) + '</span>';
    }).join('');

  // Operator pills
  document.getElementById('owner-operators-row').innerHTML =
    '<span style="font-family:\'Sweet Sans Pro\',sans-serif;font-size:9px;text-transform:uppercase;letter-spacing:0.08em;color:var(--text-faint);margin-right:8px">Operators</span>' +
    (o.brands_operated || []).map(function(b) {
      return '<span class="brand-meta-pill">' + getBrandLogoImg(b, 14) + fmt.esc(b) + '</span>';
    }).join('');

  // Portfolio title
  document.getElementById('owner-portfolio-title').textContent = o.name + ' Hotel Portfolio (' + (o.total_hotels || 0) + ' hotels'
    + (o.pipeline_hotels ? ', ' + o.pipeline_hotels + ' in the pipeline' : '') + ')';

  // Portfolio table
  ownerPortfolioSort = { col: null, dir: 1 };
  renderOwnerPortfolioTable(o.hotels || []);

  // Wire sort headers
  document.querySelectorAll('#owner-portfolio-table th[data-sort]').forEach(function(th) {
    th.onclick = function() {
      var col = th.dataset.sort;
      if (ownerPortfolioSort.col === col) {
        ownerPortfolioSort.dir *= -1;
      } else {
        ownerPortfolioSort.col = col;
        ownerPortfolioSort.dir = 1;
      }
      renderOwnerPortfolioTable(ownerDetailData.hotels || []);
    };
  });

  // Back button
  document.getElementById('owner-back-btn').onclick = function() {
    document.getElementById('screen-owner-detail').style.display = 'none';
    document.getElementById('owners-kpi-row').style.display = '';
    document.getElementById('owners-grid').style.display = '';
  };
}

function renderOwnerPortfolioTable(hotels) {
  var sorted = hotels.slice();
  if (ownerPortfolioSort.col) {
    var col = ownerPortfolioSort.col;
    var dir = ownerPortfolioSort.dir;
    sorted.sort(function(a, b) {
      var av = a[col] || '';
      var bv = b[col] || '';
      if (col === 'keys') { av = Number(av) || 0; bv = Number(bv) || 0; }
      if (av < bv) return -1 * dir;
      if (av > bv) return 1 * dir;
      return 0;
    });
  }

  var tbody = document.getElementById('owner-portfolio-tbody');
  tbody.innerHTML = sorted.map(function(h) {
    var nameCell = h.hotel_id
      ? '<span class="owner-hotel-link" onclick="showHotelDetail(' + h.hotel_id + ')">' + fmt.esc(h.name) + '</span>'
      : fmt.esc(h.name);
    if (h.pipeline) {
      nameCell += ' <span class="pill--grey owner-pipe-pill" title="Not open yet: in the pipeline, not counted in the totals">'
        + fmt.esc(h.label || h.pipeline_status || 'Pipeline')
        + (h.expected_opening ? ' · ' + h.expected_opening : '') + '</span>';
    }
    return '<tr' + (h.pipeline ? ' class="owner-row-pipe"' : '') + '>' +
      '<td>' + nameCell + '</td>' +
      '<td>' + getBrandLogoImg(h.brand_group, 14) + fmt.esc(h.brand_group || '—') + '</td>' +
      '<td>' + fmt.esc(h.city || '—') + '</td>' +
      '<td>' + getSegmentBadgeHtml(h.category || '—') + '</td>' +
      '<td style="text-align:right">' + (h.under_renovation || h.seasonal_closure ? hotelRooms(h) : h.keys ? h.keys.toLocaleString() : '—') + '</td>' +
    '</tr>';
  }).join('');
}

// Wire up export button clicks
document.getElementById('btn-export-hotels')  ?.addEventListener('click', exportHotels);
document.getElementById('btn-export-pipeline') ?.addEventListener('click', exportPipeline);
document.getElementById('btn-export-brands')   ?.addEventListener('click', exportBrands);
document.getElementById('btn-export-tourism')  ?.addEventListener('click', exportTourism);

boot();

// ═══════════════════════════════════════════════════════════════════
// VALUATION SCREEN
// ═══════════════════════════════════════════════════════════════════

const SEGMENT_DEFAULTS = {
  'Ultra Luxury': {
    rooms_rev_pct: 55, fb_rev_pct: 30,
    dept_expense_pct: 28, undist_expense_pct: 22,
    mgmt_fee_pct: 4, ffe_reserve_pct: 5,
    discount_rate: 8.5, terminal_cap_rate: 5.5,
    base_occupancy: 68, base_adr: 8000,
    revenue_growth: 3.5
  },
  'Luxury': {
    rooms_rev_pct: 60, fb_rev_pct: 28,
    dept_expense_pct: 30, undist_expense_pct: 24,
    mgmt_fee_pct: 3.5, ffe_reserve_pct: 4.5,
    discount_rate: 7.0, terminal_cap_rate: 6.0,
    base_occupancy: 65, base_adr: 4500,
    revenue_growth: 3.5
  },
  'Upper Upscale': {
    rooms_rev_pct: 65, fb_rev_pct: 22,
    dept_expense_pct: 32, undist_expense_pct: 26,
    mgmt_fee_pct: 3.0, ffe_reserve_pct: 4.0,
    discount_rate: 7.0, terminal_cap_rate: 6.5,
    base_occupancy: 63, base_adr: 2800,
    revenue_growth: 3.5
  },
  'Upscale': {
    rooms_rev_pct: 70, fb_rev_pct: 18,
    dept_expense_pct: 34, undist_expense_pct: 28,
    mgmt_fee_pct: 3.0, ffe_reserve_pct: 4.0,
    discount_rate: 7.5, terminal_cap_rate: 7.0,
    base_occupancy: 60, base_adr: 1800,
    revenue_growth: 3.5
  },
  'Midscale': {
    rooms_rev_pct: 78, fb_rev_pct: 12,
    dept_expense_pct: 36, undist_expense_pct: 30,
    mgmt_fee_pct: 2.5, ffe_reserve_pct: 3.5,
    discount_rate: 8.0, terminal_cap_rate: 7.5,
    base_occupancy: 58, base_adr: 1000,
    revenue_growth: 3.5
  }
};

// ─── Number formatting helpers ───────────────────────────────────────
function fmtMAD(val) {
  if (val >= 1e9) return 'MAD ' + (val/1e9).toFixed(1) + 'B';
  if (val >= 1e6) return 'MAD ' + (val/1e6).toFixed(1) + 'M';
  if (val >= 1e3) return 'MAD ' + (val/1e3).toFixed(0) + 'K';
  return 'MAD ' + val.toFixed(0);
}
function fmtPct(val) { return val.toFixed(1) + '%'; }
function fmtMultiple(val) { return val.toFixed(2) + 'x'; }
function fmtEUR(madVal) { return '€' + (madVal/10.8/1000).toFixed(0) + 'K'; }

// ─── Calculation engine ──────────────────────────────────────────────
// static/js/valuation_engine.js: v1 as shown today, v2 corrected behind the
// VALUATION_V2 flag (flags.py), off until approved.
const valVersion = () => (window.KODO_FLAGS && window.KODO_FLAGS.VALUATION_V2) ? 'v2' : 'v1';
function generateCashFlows(inputs) { return KodoValuation.run(inputs, valVersion()); }
function calculateIRR(cfs) { return KodoValuation.irr(cfs); }

function generateSensitivityTables(inputs, baseResults) {
  const occs = [55, 60, 65, 70, 75];
  const caps = [5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0];

  const irrTable = [];
  const valTable = [];

  occs.forEach(occ => {
    const irrRow = [];
    const valRow = [];
    caps.forEach(cap => {
      const res = generateCashFlows({
        ...inputs,
        stabilized_occ: occ,
        terminal_cap_rate: cap
      });
      irrRow.push(res.irr);
      valRow.push(res.reconciled / 1e6);
    });
    irrTable.push(irrRow);
    valTable.push(valRow);
  });

  return { occs, caps, irrTable, valTable };
}

// ─── Screen state & DOM helpers ──────────────────────────────────────
let valuationInited = false;
const valState = {
  mode: 'quick',
  customCashFlows: null,   // array of row objects when in custom mode
  lastInputs: null,
  lastResults: null,
};

function valEl(id) { return document.getElementById(id); }
function valNum(id) { return parseFloat(valEl(id).value) || 0; }

function valSensClass(irrPct) {
  if (irrPct > 18) return 'val-sens-high';
  if (irrPct >= 14) return 'val-sens-mid-high';
  if (irrPct >= 10) return 'val-sens-mid';
  return 'val-sens-low';
}

function valNearestIdx(arr, target) {
  let best = 0, bestDiff = Infinity;
  arr.forEach((v, i) => {
    const d = Math.abs(v - target);
    if (d < bestDiff) { bestDiff = d; best = i; }
  });
  return best;
}

// ─── Init ─────────────────────────────────────────────────────────────
function initValuation() {
  if (!valuationInited) {
    valuationInited = true;
    valBuildCityOptions();
    valWireEvents();
    valApplySegmentDefaults('Luxury', /*silent=*/true);
    valUpdateLiveMetrics();
  }
  valApplyTierGating();
}

function valBuildCityOptions() {
  const sel = valEl('val-p-city');
  if (!sel || sel.options.length > 1) return;
  const cities = [...new Set((hotels || []).map(h => h.city))].sort();
  cities.forEach(city => {
    const o = document.createElement('option');
    o.value = city; o.textContent = city;
    sel.appendChild(o);
  });
}

// ─── Tier gating ──────────────────────────────────────────────────────
function valApplyTierGating() {
  const tier = (window._kodoUser && window._kodoUser.tier) || '';
  const panel = valEl('val-input-panel');

  // Remove any existing overlay first
  const existingOverlay = document.getElementById('val-observer-overlay');
  if (existingOverlay) existingOverlay.remove();

  if (tier === 'observer') {
    panel.style.position = 'relative';
    const overlay = document.createElement('div');
    overlay.id = 'val-observer-overlay';
    overlay.className = 'val-lock-overlay';
    overlay.innerHTML = `
      <div class="val-lock-card">
        <div class="val-lock-label">Upgrade Required</div>
        <div class="val-lock-title">Hotel Valuation Tool</div>
        <div class="val-lock-body">DCF modelling, income capitalization, and sensitivity analysis are available on the Benchmarker and Advisory plans.</div>
        <a href="/#pricing" class="val-lock-cta">Upgrade now →</a>
      </div>`;
    panel.appendChild(overlay);
    panel.querySelectorAll('input, select, button').forEach(el => {
      if (el.id !== 'val-mode-quick-btn') el.disabled = true;
    });
  } else {
    panel.querySelectorAll('input, select, button').forEach(el => { el.disabled = false; });
  }

  const customLock = valEl('val-mode-custom-lock');
  if (tier === 'observer' || tier === 'benchmarker') {
    customLock.style.display = '';
  } else {
    customLock.style.display = 'none';
  }

  // If currently on custom mode but tier no longer allows it, bounce back
  if (valState.mode === 'custom' && tier !== 'advisory') {
    valSwitchMode('quick');
  }

  // Sensitivity — Advisory only
  const sensSection = valEl('val-sensitivity-section');
  const existingSensOverlay = document.getElementById('val-sens-overlay');
  if (existingSensOverlay) existingSensOverlay.remove();
  if (tier !== 'advisory') {
    sensSection.style.position = 'relative';
    const overlay = document.createElement('div');
    overlay.id = 'val-sens-overlay';
    overlay.className = 'val-lock-overlay';
    overlay.style.position = 'absolute';
    overlay.innerHTML = `
      <div class="val-lock-card">
        <div class="val-lock-label">Advisory Only</div>
        <div class="val-lock-title">Sensitivity Tables</div>
        <div class="val-lock-body">IRR and value sensitivity grids across occupancy and cap-rate scenarios are available on the Advisory plan.</div>
        <a href="/#pricing" class="val-lock-cta">Upgrade now →</a>
      </div>`;
    sensSection.appendChild(overlay);
  }

  // Export — Advisory only
  const exportBtn = valEl('val-export-btn');
  exportBtn.disabled = (tier !== 'advisory');
}

// ─── Segment defaults ─────────────────────────────────────────────────
function valApplySegmentDefaults(segment, silent) {
  const d = SEGMENT_DEFAULTS[segment];
  if (!d) return;
  valEl('val-q-occ').value = d.base_occupancy;
  valEl('val-q-adr').value = d.base_adr;
  valEl('val-q-growth').value = d.revenue_growth;
  valEl('val-q-rooms-pct').value = d.rooms_rev_pct;
  valEl('val-q-fb-pct').value = d.fb_rev_pct;
  valEl('val-q-dept-pct').value = d.dept_expense_pct;
  valEl('val-q-undist-pct').value = d.undist_expense_pct;
  valEl('val-q-mgmt-pct').value = d.mgmt_fee_pct;
  valEl('val-q-ffe-pct').value = d.ffe_reserve_pct;
  valEl('val-discount').value = d.discount_rate;
  valEl('val-termcap').value = d.terminal_cap_rate;
  valEl('val-gen-occ').value = d.base_occupancy;
  valEl('val-gen-adr').value = d.base_adr;
  valEl('val-gen-growth').value = d.revenue_growth;
  valUpdateLiveMetrics();
}

// ─── Live readouts (before Run Valuation) ────────────────────────────
function valUpdateLiveMetrics() {
  const occ = valNum('val-q-occ');
  const adr = valNum('val-q-adr');
  valEl('val-q-occ-val').textContent = occ + '%';
  valEl('val-q-growth-val').textContent = valNum('val-q-growth') + '%/yr';
  valEl('val-q-rooms-pct-val').textContent = valNum('val-q-rooms-pct') + '%';
  valEl('val-q-fb-pct-val').textContent = valNum('val-q-fb-pct') + '%';
  valEl('val-q-dept-pct-val').textContent = valNum('val-q-dept-pct') + '%';
  valEl('val-q-undist-pct-val').textContent = valNum('val-q-undist-pct') + '%';
  valEl('val-q-mgmt-pct-val').textContent = valNum('val-q-mgmt-pct') + '%';
  valEl('val-q-ffe-pct-val').textContent = valNum('val-q-ffe-pct') + '%';
  valEl('val-txn-pct-val').textContent = valNum('val-txn-pct') + '%';
  valEl('val-discount-val').textContent = fmtPct(valNum('val-discount'));
  valEl('val-termcap-val').textContent = fmtPct(valNum('val-termcap'));
  valEl('val-equity-val').textContent = valNum('val-equity') + '%';
  valEl('val-debt').value = (100 - valNum('val-equity')) + '%';
  valEl('val-loanrate-val').textContent = fmtPct(valNum('val-loanrate'));
  valEl('val-taxrate-val').textContent = valNum('val-taxrate') + '%';

  const revpar = adr * occ / 100;
  valEl('val-q-revpar').value = fmtMAD(revpar) + ' /night';

  // GOP / NOI margin preview using current P&L sliders
  const roomsPct = valNum('val-q-rooms-pct') / 100;
  const totalRevProxy = roomsPct > 0 ? 1 / roomsPct : 1; // per-unit-rooms-rev basis
  const deptExp   = valNum('val-q-dept-pct') / 100;      // % of rooms rev
  const undistExp = valNum('val-q-undist-pct') / 100;    // % of total rev
  const mgmtFee   = valNum('val-q-mgmt-pct') / 100;
  const ffe       = valNum('val-q-ffe-pct') / 100;
  const gop = totalRevProxy - deptExp - undistExp * totalRevProxy - mgmtFee * totalRevProxy;
  const gopMargin = gop / totalRevProxy;
  const noiMargin = gopMargin - ffe;

  const gopEl = valEl('val-q-gop-margin');
  const noiEl = valEl('val-q-noi-margin');
  gopEl.textContent = fmtPct(gopMargin * 100);
  noiEl.textContent = fmtPct(noiMargin * 100);
  gopEl.className = 'val-metric-value ' + (gopMargin >= 0.30 ? 'val-metric-good pill--green' : gopMargin >= 0.20 ? 'val-metric-mid' : 'val-metric-poor pill--red');
  noiEl.className = 'val-metric-value ' + (noiMargin >= 0.26 ? 'val-metric-good pill--green' : noiMargin >= 0.16 ? 'val-metric-mid' : 'val-metric-poor pill--red');
}

// ─── Mode switching ───────────────────────────────────────────────────
function valSwitchMode(mode) {
  const tier = (window._kodoUser && window._kodoUser.tier) || '';
  if (mode === 'custom' && tier !== 'advisory') {
    if (typeof showUpgradeModal === 'function') {
      showUpgradeModal('Advisory Only', 'Custom Cash Flows mode — build and edit a fully custom 10-year projection — is available on the Advisory plan.');
    }
    return;
  }
  valState.mode = mode;
  document.querySelectorAll('.val-mode-btn').forEach(b => b.classList.toggle('active', b.dataset.mode === mode));
  document.querySelectorAll('.val-mode-panel').forEach(p => p.classList.toggle('active', p.dataset.mode === mode));
}

// ─── Gather inputs from the DOM ──────────────────────────────────────
function valGatherInputs() {
  const keys = Math.max(1, valNum('val-p-keys'));
  const equity_pct = valNum('val-equity');
  return {
    keys,
    stabilized_occ: valNum('val-q-occ'),
    adr: valNum('val-q-adr'),
    growth_rate: valNum('val-q-growth'),
    rampup: valNum('val-q-rampup'),
    rooms_rev_pct: valNum('val-q-rooms-pct'),
    fb_rev_pct: valNum('val-q-fb-pct'),
    dept_exp_pct: valNum('val-q-dept-pct'),
    undist_exp_pct: valNum('val-q-undist-pct'),
    mgmt_fee_pct: valNum('val-q-mgmt-pct'),
    ffe_pct: valNum('val-q-ffe-pct'),
    discount_rate: valNum('val-discount'),
    terminal_cap_rate: valNum('val-termcap'),
    hold_period: valState.holdPeriod || 10,
    capex_yr1: valNum('val-capex'),
    purchase_price: valNum('val-price'),
    equity_pct,
    txn_pct: valNum('val-txn-pct'),
    loan_rate: valNum('val-loanrate'),
  };
}

// ─── Run Valuation ────────────────────────────────────────────────────
function valRunValuation() {
  const inputs = valGatherInputs();
  valState.lastInputs = inputs;

  let results;
  if (valState.mode === 'custom' && valState.customCashFlows) {
    results = valComputeFromCustomCashFlows(inputs, valState.customCashFlows);
  } else {
    results = generateCashFlows(inputs);
    valState.customCashFlows = null;
  }
  valState.lastResults = results;

  valEl('val-placeholder').style.display = 'none';
  valEl('val-results').classList.add('active');

  valRenderKPICards(inputs, results);
  valRenderCashFlowTable(inputs, results, valState.mode === 'custom');
  valRenderApproachCards(inputs, results);

  const tier = (window._kodoUser && window._kodoUser.tier) || '';
  if (tier === 'advisory') {
    const sens = generateSensitivityTables(inputs, results);
    valRenderSensitivityTables(inputs, sens);
  }
}

// Recompute NPV/IRR/etc. from a (possibly hand-edited) cash flow array
function valComputeFromCustomCashFlows(inputs, cashFlows) {
  return KodoValuation.fromCashFlows(inputs, cashFlows, valVersion());
}

// ─── Render: KPI cards ────────────────────────────────────────────────
function valRenderKPICards(inputs, results) {
  valEl('val-kpi-value').textContent = `${fmtMAD(results.range_low)} — ${fmtMAD(results.range_high)}`;
  valEl('val-kpi-perkey').textContent = fmtMAD(results.value_per_key);
  valEl('val-kpi-perkey-eur').textContent = `${fmtEUR(results.value_per_key)} equivalent (÷10.8)`;
  valEl('val-kpi-irr').textContent = fmtPct(results.irr);
  valEl('val-kpi-irr-sub').textContent = `${inputs.hold_period}-year hold period`;
  valEl('val-kpi-multiple').textContent = fmtMultiple(results.equity_multiple);
  // VALUATION_V2: the range comes from the inputs' sensitivity, and every assumption is listed
  const box = valEl('val-assumptions');
  if (box) {
    box.hidden = results.version !== 'v2';
    if (results.version === 'v2') {
      valEl('val-kpi-irr-sub').textContent = `${inputs.hold_period}-year hold · unlevered, before tax`;
      valEl('val-kpi-multiple-sub').textContent = `levered: ${inputs.equity_pct}% equity, debt at ${inputs.loan_rate}%`;
      box.innerHTML = '<div class="val-assumptions-title">Assumptions</div><ul>'
        + KodoValuation.assumptions(inputs).map(a => `<li>${fmt.esc(a)}</li>`).join('') + '</ul>';
    }
  }
}

// ─── Render: Cash flow table ──────────────────────────────────────────
function valRenderCashFlowTable(inputs, results, editable) {
  valEl('val-cf-title').textContent = `${inputs.hold_period}-Year Projected Cash Flows · MAD`;
  valEl('val-reset-btn').style.display = editable ? '' : 'none';

  const tbody = valEl('val-cf-tbody');
  tbody.innerHTML = '';

  results.cashFlows.forEach((cf, i) => {
    const tr = document.createElement('tr');
    tr.dataset.row = i;
    const ed = editable;
    tr.innerHTML = `
      <td>Year ${cf.yr}</td>
      <td ${ed ? 'contenteditable="true" data-field="occ"' : ''}>${cf.occ.toFixed(1)}</td>
      <td ${ed ? 'contenteditable="true" data-field="adr"' : ''}>${Math.round(cf.adr).toLocaleString('en')}</td>
      <td data-field="revpar">${Math.round(cf.revpar).toLocaleString('en')}</td>
      <td ${ed ? 'contenteditable="true" data-field="total_rev"' : ''}>${Math.round(cf.total_rev).toLocaleString('en')}</td>
      <td>${Math.round(cf.rooms_rev).toLocaleString('en')}</td>
      <td>${Math.round(cf.fb_rev).toLocaleString('en')}</td>
      <td ${ed ? 'contenteditable="true" data-field="gop"' : ''}>${Math.round(cf.gop).toLocaleString('en')}</td>
      <td data-field="gop_margin">${cf.gop_margin.toFixed(1)}</td>
      <td ${ed ? 'contenteditable="true" data-field="noi"' : ''}>${Math.round(cf.noi).toLocaleString('en')}</td>
      <td ${ed ? 'contenteditable="true" data-field="fcf"' : ''}>${Math.round(cf.fcf).toLocaleString('en')}</td>
      <td data-field="pv_fcf">${Math.round(cf.pv_fcf).toLocaleString('en')}</td>
    `;
    tbody.appendChild(tr);
  });

  // Terminal Value row — spans Occ..NOI, shows raw terminal value in the
  // FCF column and its discounted value in PV(FCF)
  const trTerm = document.createElement('tr');
  trTerm.className = 'val-terminal-row';
  trTerm.innerHTML =
    '<td>Terminal Value</td>' +
    '<td colspan="9"></td>' +
    `<td>${Math.round(results.terminal_value).toLocaleString('en')}</td>` +
    `<td>${Math.round(results.pv_terminal).toLocaleString('en')}</td>`;
  tbody.appendChild(trTerm);

  // NPV total row
  const trTotal = document.createElement('tr');
  trTotal.className = 'val-total-row';
  const npvTotal = results.total_pv_fcf + results.pv_terminal;
  trTotal.innerHTML = `<td>NPV Total</td><td colspan="10"></td><td>${Math.round(npvTotal).toLocaleString('en')}</td>`;
  tbody.appendChild(trTotal);

  if (editable) {
    tbody.querySelectorAll('td[contenteditable="true"]').forEach(td => {
      td.addEventListener('blur', valOnCellEdit);
    });
  }
}

// Re-derive a row + recompute totals when a Mode-2 cell is edited
function valOnCellEdit(e) {
  const td = e.target;
  const tr = td.closest('tr');
  const rowIdx = parseInt(tr.dataset.row, 10);
  if (isNaN(rowIdx) || !valState.customCashFlows) return;

  const field = td.dataset.field;
  const raw = parseFloat(td.textContent.replace(/,/g, ''));
  if (isNaN(raw)) { valRunValuation(); return; }

  const row = valState.customCashFlows[rowIdx];
  row[field] = raw;

  // Derived, non-editable fields
  row.revpar = row.adr * row.occ / 100;
  row.gop_margin = row.total_rev ? (row.gop / row.total_rev) * 100 : 0;
  const discount_rate = valNum('val-discount');
  row.pv_fcf = row.fcf / Math.pow(1 + discount_rate / 100, row.yr);

  valRunValuation();
}

// ─── Render: Valuation approach cards ─────────────────────────────────
function valRenderApproachCards(inputs, results) {
  const stab_yr = results.cashFlows[Math.min(2, results.cashFlows.length - 1)];
  valEl('val-ic-noi').textContent   = fmtMAD(stab_yr.noi);
  valEl('val-ic-cap').textContent   = fmtPct(inputs.terminal_cap_rate);
  valEl('val-ic-value').textContent = fmtMAD(results.income_cap_value);
  valEl('val-ic-perkey').textContent = fmtMAD(results.income_cap_value / inputs.keys);

  valEl('val-dcf-title').textContent  = `DCF Analysis · ${inputs.hold_period}-Year Hold`;
  valEl('val-dcf-pvcf').textContent   = fmtMAD(results.total_pv_fcf);
  valEl('val-dcf-pvterm').textContent = fmtMAD(results.pv_terminal);
  valEl('val-dcf-value').textContent  = fmtMAD(results.dcf_value);
  valEl('val-dcf-irr').textContent    = fmtPct(results.irr);
  valEl('val-dcf-multiple').textContent = fmtMultiple(results.equity_multiple);
  valEl('val-dcf-payback').textContent  = results.payback.toFixed(1) + ' years';

  valEl('val-rec-value').textContent  = `${fmtMAD(results.range_low)} — ${fmtMAD(results.range_high)}`;
  valEl('val-rec-perkey').textContent = `${fmtMAD(results.value_per_key)} / key · ${fmtEUR(results.value_per_key)}`;
}

// ─── Render: Sensitivity tables ────────────────────────────────────────
function valRenderSensitivityTables(inputs, sens) {
  const curOccIdx = valNearestIdx(sens.occs, inputs.stabilized_occ);
  const curCapIdx = valNearestIdx(sens.caps, inputs.terminal_cap_rate);

  const buildTable = (table, matrix, fmt, currentSuffix) => {
    let html = '<thead><tr><th>Occ \\ Cap</th>' +
      sens.caps.map(c => `<th>${c.toFixed(1)}%</th>`).join('') + '</tr></thead><tbody>';
    sens.occs.forEach((occ, i) => {
      html += `<tr><th>${occ}%</th>`;
      sens.caps.forEach((cap, j) => {
        const irrVal = sens.irrTable[i][j];
        const cls = valSensClass(irrVal);
        const isCurrent = (i === curOccIdx && j === curCapIdx);
        html += `<td class="${cls}${isCurrent ? ' val-sens-current' : ''}">${fmt(matrix[i][j])}</td>`;
      });
      html += '</tr>';
    });
    html += '</tbody>';
    table.innerHTML = html;
  };

  buildTable(valEl('val-sens-irr-table'), sens.irrTable, v => fmtPct(v));
  buildTable(valEl('val-sens-val-table'), sens.valTable, v => v.toFixed(1) + 'M');
}

// ─── Generate starting point (Mode 2) ─────────────────────────────────
function valGenerateCustomTable() {
  const segment = valEl('val-gen-segment').value || 'Luxury';
  // Keep the shared growth field in sync so valRunValuation()'s later
  // re-gather (used for the terminal value extrapolation) matches
  // what this table was actually generated with.
  valEl('val-q-growth').value = valEl('val-gen-growth').value;
  const inputs = valGatherInputs();
  inputs.stabilized_occ = valNum('val-gen-occ');
  inputs.adr = valNum('val-gen-adr');
  inputs.growth_rate = valNum('val-gen-growth');
  const d = SEGMENT_DEFAULTS[segment];
  if (d) {
    inputs.rooms_rev_pct   = d.rooms_rev_pct;
    inputs.fb_rev_pct      = d.fb_rev_pct;
    inputs.dept_exp_pct    = d.dept_expense_pct;
    inputs.undist_exp_pct  = d.undist_expense_pct;
    inputs.mgmt_fee_pct    = d.mgmt_fee_pct;
    inputs.ffe_pct         = d.ffe_reserve_pct;
  }
  const results = generateCashFlows(inputs);
  valState.customCashFlows = results.cashFlows.map(cf => ({ ...cf }));
  valState.lastInputs = inputs;
  valRunValuation();
}

// ─── Event wiring ──────────────────────────────────────────────────────
function valWireEvents() {
  // Mode toggle
  valEl('val-mode-quick-btn').addEventListener('click', () => valSwitchMode('quick'));
  valEl('val-mode-custom-btn').addEventListener('click', () => valSwitchMode('custom'));

  // Segment auto-fill
  valEl('val-p-segment').addEventListener('change', e => {
    if (e.target.value) valApplySegmentDefaults(e.target.value, false);
  });

  // Live-updating sliders/inputs
  ['val-q-occ','val-q-growth','val-q-rooms-pct','val-q-fb-pct','val-q-dept-pct',
   'val-q-undist-pct','val-q-mgmt-pct','val-q-ffe-pct','val-q-adr','val-txn-pct',
   'val-discount','val-termcap','val-equity','val-loanrate','val-taxrate']
    .forEach(id => valEl(id).addEventListener('input', valUpdateLiveMetrics));

  // Hold period toggle
  valEl('val-hold-toggle').addEventListener('click', e => {
    const btn = e.target.closest('.val-toggle-btn');
    if (!btn) return;
    valEl('val-hold-toggle').querySelectorAll('.val-toggle-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    valState.holdPeriod = parseInt(btn.dataset.hold, 10);
  });
  valState.holdPeriod = 10;

  // Advanced financing
  valEl('val-adv-toggle').addEventListener('click', () => {
    valEl('val-adv-panel').classList.toggle('open');
  });
  valEl('val-recalc-wacc-btn').addEventListener('click', () => {
    const equity = valNum('val-equity');
    const debt = 100 - equity;
    const loanRate = valNum('val-loanrate');
    const taxRate = valNum('val-taxrate');
    const segment = valEl('val-p-segment').value || 'Luxury';
    const ke = (SEGMENT_DEFAULTS[segment] || SEGMENT_DEFAULTS['Luxury']).discount_rate;
    const wacc = (equity / 100) * ke + (debt / 100) * loanRate * (1 - taxRate / 100);
    valEl('val-discount').value = wacc.toFixed(1);
    valUpdateLiveMetrics();
  });

  // Mode 2 — generate starting point
  valEl('val-generate-toggle-btn').addEventListener('click', () => {
    valEl('val-generate-form').classList.toggle('open');
  });
  valEl('val-generate-run-btn').addEventListener('click', valGenerateCustomTable);

  // Reset (Mode 2)
  valEl('val-reset-btn').addEventListener('click', () => {
    if (valState.mode === 'custom') valGenerateCustomTable();
  });

  // Run valuation
  valEl('val-run-btn').addEventListener('click', valRunValuation);

  // Export
  valEl('val-export-btn').addEventListener('click', valExportPDF);
}

// ─── PDF export ─────────────────────────────────────────────────────────
async function valExportPDF() {
  const tier = (window._kodoUser && window._kodoUser.tier) || '';
  if (tier !== 'advisory') {
    if (typeof showUpgradeModal === 'function') {
      showUpgradeModal('Advisory Only', 'PDF valuation reports are available on the Advisory plan.');
    }
    return;
  }
  if (!valState.lastResults || !valState.lastInputs) {
    if (typeof showUpgradeModal === 'function') {
      showUpgradeModal('Run a valuation first', 'Configure your inputs and click Run Valuation before exporting a report.');
    }
    return;
  }

  const btn = valEl('val-export-btn');
  const originalText = btn.textContent;
  btn.disabled = true;
  btn.textContent = 'Generating…';

  try {
    const property = {
      name: valEl('val-p-name').value || 'Unnamed Property',
      city: valEl('val-p-city').value || '—',
      segment: valEl('val-p-segment').value || '—',
      keys: valNum('val-p-keys'),
      year_built: valEl('val-p-year').value || null,
    };

    const sensitivity = generateSensitivityTables(valState.lastInputs, valState.lastResults);

    const r = await fetch('/api/valuation/export', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        property,
        inputs: valState.lastInputs,
        results: valState.lastResults,
        sensitivity,
        mode: valState.mode,
      }),
    });

    if (!r.ok) {
      const err = await r.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(err.error || 'Export failed');
    }

    const blob = await r.blob();
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    const safeName = property.name.replace(/[^a-z0-9]+/gi, '_');
    a.href = url;
    a.download = `Kodo_Valuation_${safeName}.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } catch (err) {
    if (typeof showUpgradeModal === 'function') {
      showUpgradeModal('Export failed', err.message);
    }
  } finally {
    btn.disabled = false;
    btn.textContent = originalText;
  }
}
