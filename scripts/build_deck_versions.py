"""Build editable audience editions from the current HTML deck. No dependencies."""
from pathlib import Path
import html
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / 'Mumbot World Pitch Deck.html').read_text(encoding='utf-8')
SECTIONS = re.findall(r'<section\b[^>]*data-label="[^"]+"[\s\S]*?</section>', SOURCE)
SOURCE_NOTES = json.loads(re.search(r'<script type="application/json" id="speaker-notes">([\s\S]*?)</script>', SOURCE)[1])
BASE = {}
for index, section in enumerate(SECTIONS):
    label = html.unescape(re.search(r'data-label="([^"]+)"', section)[1])
    label = re.sub(r'^A\d+ · ', '', label)
    BASE[label] = (section, SOURCE_NOTES[index])


def copy(label, replacements=(), note=None):
    markup, original_note = BASE[label]
    markup = re.sub(r' data-appendix="true"', '', markup)
    markup = re.sub(r'data-label="[^"]+"', f'data-label="{html.escape(label)}"', markup, count=1)
    for before, after in replacements:
        if before not in markup:
            raise ValueError(f'Missing replacement in {label}: {before}')
        markup = markup.replace(before, after)
    return [markup, original_note if note is None else note]


def new(label, classes, content, status, note='Proposed format and scope for discussion. Final deliverables and commercial terms require an agreed brief.'):
    return [f'''<section data-label="{html.escape(label)}" class="bg-bark grain rev {classes}">
<div class="corner-mark tl mono">{html.escape(label.upper())}</div>
<div class="corner-mark tr mono">{html.escape(status)}</div>
{content}
</section>''', note]


def head(title, lead):
    return f'<header class="rev-head"><h2 class="mumbot">{title}</h2><p>{lead}</p></header>'


def rows(label, title, lead, items, footer, status='PROPOSED APPROACH', note=None):
    content = head(title, lead) + '<div class="v-table">'
    for name, text, detail in items:
        content += f'<div class="v-row"><h3>{name}</h3><p>{text}</p><p>{detail}</p></div>'
    content += f'</div><div class="v-footer">{footer}</div>'
    kwargs = {} if note is None else {'note': note}
    return new(label, 'v-rows', content, status, **kwargs)


def columns(label, title, lead, items, footer, status='PROPOSED APPROACH'):
    content = head(title, lead) + '<div class="v-columns">'
    for name, text, detail_label, detail in items:
        content += f'<div class="v-column"><h3>{name}</h3><p>{text}</p><p class="v-detail"><b>{detail_label}</b>{detail}</p></div>'
    content += f'</div><div class="v-footer">{footer}</div>'
    return new(label, 'v-columns-slide', content, status)


def intro(label, title, statement, details, eyebrow, status):
    markup = f'''<section data-label="{html.escape(label)}" class="bg-parchment grain product-intro v-intro">
<div class="corner-mark tl mono">{html.escape(label.upper())}</div><div class="corner-mark tr mono">{html.escape(status)}</div>
<div class="eyebrow">{eyebrow}</div><h2 class="mumbot">{title}</h2>
<p class="product-statement">{statement}</p><div class="product-details">'''
    for title, text in details:
        markup += f'<div><span class="detail-label">{title}</span><p>{text}</p></div>'
    return [markup + '</div></section>', 'Audience-specific positioning. Browser gatherings and new exhibition or sponsor formats are proposed, subject to scope and readiness.']


def cover(audience, subtitle, format, stage, edition='Web'):
    return copy('Cover', [
        ('class="bg-bark grain cover"', 'class="bg-bark grain cover v-cover"'),
        ('A PITCH FROM THE FOREST FLOOR · 2026', f'{audience.upper()} · 2026'),
        ('A shared world of art, play and gathering.', subtitle),
        ('<span class="game">Web</span>', f'<span class="game">{edition}</span>'),
        ('Browser-based world', format),
        ('Phase 01 · Funding proposal', stage),
        ('<span>Stage<b>', '<span>Discussion<b>'),
    ])


def close(title, invite, next_step):
    return copy('Closing', [
        ('class="bg-parchment grain closing"', 'class="bg-parchment grain closing v-closing"'),
        ('Thank you for<br/>walking with us', title),
        ('Contact us to discuss Phase 01 funding or a creative partnership.', invite),
        ('<div class="contacts">', f'<p class="v-next">{next_step}</p><div class="contacts">'),
    ])


def team(footer):
    return copy('Core Team', [('ADDITIONAL MUSIC AND VOICE CONTRIBUTORS · SEE APPENDIX A7', footer)])


investor_revenue = rows('Business Model', 'How the world<br/>could earn',
    'Begin with collectible releases and paid creative work. Test whether each can contribute to operating the browser world.', [
    ('Collectibles', 'Collectors purchase physical editions through existing commerce. Optional digital companions follow reliable ownership and inventory features.', 'Agree the share allocated to the hub for each release. Track manufacturing, fulfillment and partner costs.'),
    ('Paid creative<br/>work', 'Brands and cultural partners commission gatherings, artist releases or temporary spaces.', 'Quote production and hosting against a defined scope. Track creative time, support costs and contribution after delivery.'),
    ('Installations', 'Venues commission an adaptation of the world for a physical presentation, with a defined exhibition period.', 'Price the presentation and technical support separately from equipment, venue and travel costs.'),
    ], '<strong>First commercial tests:</strong> one collectible release and one paid partner experience after the core hub is ready.',
    status='REVENUE HYPOTHESES', note='Proposed business model, not contracted revenue. Existing Mumbot product sales are not automatically revenue of the browser project. Rights and each release’s revenue allocation must be agreed.')

investor_entry = columns('First Audience', 'Start with<br/>Mumbot fans',
    'The first visitors can come through Mumbot’s own creative work and relationships. Phase 01 tests whether they choose to return.', [
    ('Invite', 'Invite Mumbot collectors and Ghost Club participants into a small, hosted playtest.', 'Acquisition signal', 'Track invitations, registrations and successful first visits by source.'),
    ('Gather', 'Use an artist conversation, a new work or a collectible launch as a reason to spend time together.', 'Participation signal', 'Observe attendance, session experience and what visitors choose to explore.'),
    ('Bring people back', 'Invite the same cohort to a second gathering. Adjust the experience using their feedback.', 'Retention signal', 'Measure repeat visits within a defined window and the effort needed to host again.'),
    ], 'Start with direct invitations and partner channels. Consider paid acquisition after repeat visitation and delivery costs are understood.', 'PROPOSED LAUNCH APPROACH')

investor_validation = rows('What We Must Prove', 'What Phase 01<br/>must prove',
    'Use a small pilot to answer the questions that determine whether further investment makes sense.', [
    ('People return', 'Can visitors join reliably and find a reason to attend a second gathering?', 'Measure successful joins, participation and repeat visitation. Set evaluation criteria before the pilot.'),
    ('Partners pay', 'Will a partner commission a defined experience at a price that covers the work?', 'Record the scope, fee and delivery costs of a paid pilot. Separate sales interest from signed work.'),
    ('Costs are known', 'Can the core world support more events without rebuilding the experience each time?', 'Track recurring hosting, support time and the cost of adapting a second event.'),
    ], '<strong>Current gap:</strong> browser retention, commercial conversion and recurring delivery costs remain to be established.', 'VALIDATION BEFORE EXPANSION')

investor_growth = columns('Repeatable Program', 'Build once,<br/>host again',
    'The investment hypothesis is that a reusable world can support a continuing program of releases and commissioned experiences.', [
    ('The shared world', 'Retain the forest, character assets and tools for hosting. Improve the same core experience between events.', 'What improves', 'Reliability and the time required to prepare each gathering.'),
    ('The next program', 'Adapt proven formats for another artist, release or cultural partner. Price bespoke additions explicitly.', 'What we test', 'Partner renewal and contribution after creative work, hosting and support.'),
    ('Selective growth', 'Add regions, digital items or memberships when use and commercial evidence support the additional work.', 'Decision point', 'Expand formats with repeat demand and manageable operating costs.'),
    ], 'Artist and partner rights, production capacity and revenue allocation shape what can be repeated.', 'INVESTMENT HYPOTHESIS')

investor_ask = copy('The Ask', [
    ('class="bg-bark grain funding rev"', 'class="bg-bark grain funding rev v-funding"'),
    ('BUILD THE FIRST JOINABLE HUB', 'PHASE 01 CAPITAL REQUIREMENT'),
    ('Proposed scope and allocation; the final production budget will be agreed with the funding partner.', 'US$50,000 is the minimum for Phase 01. Investment structure, entity, rights and terms remain open for discussion.'),
], note='Investor discussion with a USD 50,000 minimum funding ask for Phase 01. No valuation, equity percentage, instrument, investment return or agreed investment terms are asserted. A detailed budget and rights position need to be established with the creators.')

investors = [
    cover('Investor discussion', 'An artist-led world with a path to recurring creative commerce.', 'Browser world &amp; creative IP', 'Phase 01 capital'),
    copy('The Product', [('Mumbot fans and collectors, the Ghost Club community, and people drawn to gentle exploration.', 'A first audience of Mumbot collectors and Ghost Club participants, with a broader audience to be tested.')]),
    copy('Audience & Releases'), copy('World & Characters'), copy('Browser Prototype'),
    investor_revenue, investor_entry, investor_validation, copy('Delivery Plan'), investor_growth,
    team('CHARACTER IP, WORLD DEVELOPMENT AND PRODUCTION LED BY THE CREATORS'), investor_ask,
    close('Back the<br/>first chapter', 'Let’s discuss the capital and milestones for Phase 01.', 'Next: a prototype walkthrough and a review of the costed scope, rights and proposed investment structure.'),
]
investor_appendix = [copy('Live Experience'), copy('Hub Possibilities'), copy('Tech'), copy('Talent Roster')]

sponsor_formats = rows('Collaboration Formats', 'Ways to<br/>collaborate',
    'Choose a format that fits the partner’s audience and gives visitors something meaningful to take part in.', [
    ('Campfire<br/>session', 'Support an artist conversation, listening session or hosted community gathering.', 'A defined program, agreed partner credit and an event recap. Contributors and music use are scoped in advance.'),
    ('Artist release', 'Pair a physical collectible or edition with an opening event and artwork from its world.', 'Production and launch support, with a route to the existing shop. Product quantities and sales share are agreed separately.'),
    ('Guest grove', 'Commission a temporary exhibition or listening space inside the forest.', 'A more involved option, scheduled after the shared hub is ready. Custom design and hosting are quoted separately.'),
    ], 'Browser events depend on Phase 01 readiness. A physical presentation can be scoped around the venue and available work.', 'ILLUSTRATIVE FORMATS')

sponsor_package = columns('Pilot Deliverables', 'A defined<br/>creative package',
    'A first collaboration can be commissioned around one program and a clear production brief.', [
    ('The experience', 'An agreed creative concept, selected artwork and one hosted program within a defined event window.', 'Set in the brief', 'Program, format, guest roles, hosting and any custom assets.'),
    ('The presentation', 'Partner credit and release materials that fit the artwork. Prepare selected assets for the agreed channels.', 'Set in the brief', 'Placements, approval process, usage period and distribution responsibilities.'),
    ('The recap', 'A concise record of what was delivered, how people participated and what a second event would improve.', 'Set in the brief', 'Metrics, attribution method and a delivery date for the recap.'),
    ], 'The proposal will specify quantities, dates, fees and rights. Audience reach is established through the pilot.', 'PROPOSED PILOT SCOPE')

sponsor_measure = rows('Measuring the Pilot', 'What we<br/>report back',
    'Agree the measures with the partner before production, then report the results of the actual event.', [
    ('Delivery', 'What ran, when it ran and which agreed creative and promotional assets were delivered.', 'Document the event and approved partner placements. Report any changes to scope.'),
    ('Participation', 'Attendance, successful joins and time spent in the experience, where measurement is available.', 'Include participant feedback and repeat attendance when a second session is held.'),
    ('Response', 'Shop referrals and attributable sales for a release, when the checkout and tracking setup support them.', 'Use tagged links or agreed codes. Compare with the baseline where one exists.'),
    ], 'The existing product audience supports the concept. Event attendance, impressions and sales are not forecast or guaranteed.', 'PILOT MEASUREMENT PLAN')

sponsor_plan = columns('Commissioning a Pilot', 'Plan the first<br/>collaboration',
    'Start with the partner’s purpose, then match the creative format to the budget and production readiness.', [
    ('Brief &amp; fit', 'Share the campaign goal, intended audience, preferred window and budget range.', 'First output', 'A proposed concept with a suitable format and readiness check.'),
    ('Scope &amp; fee', 'Agree deliverables, partner placement, approvals, rights and the production schedule.', 'Commercial model', 'A production and hosting fee. Product sales share is agreed separately.'),
    ('Produce &amp; host', 'Prepare the experience, test the setup, deliver the program and review the results together.', 'Before launch', 'Confirm technical readiness and contributor availability before announcing the event.'),
    ], 'Manufacturing, venue equipment, travel and additional promotion are scoped separately when relevant.', 'NEXT STEP: A SCOPED PROPOSAL')

sponsor_coffee = copy('Partner Experience', [
    ('<h3>How it earns</h3>', '<h3>How it is commissioned</h3>'),
    ('A production and hosting fee, with any product sales share agreed separately.', 'A production and hosting fee for the agreed program. Any product sales share is agreed separately.'),
])

sponsors = [
    cover('Sponsor partnership', 'Artist-led experiences that bring people together.', 'Gatherings &amp; artist releases', 'A first collaboration', 'Partnerships'),
    intro('The Sponsor Opportunity', 'Meet around<br/>the campfire',
          'Commission a gathering, collectible release or temporary space within Mumbot’s world of art and characters.', [
          ('PARTNER FIT', 'Culture, music, design and collectible brands with a clear connection to the work and its community.'),
          ('EXISTING FOUNDATION', 'Character artwork and products, an established creative community and a physical installation example.'),
          ('PRODUCTION READINESS', 'Browser gatherings follow a tested, joinable build. Physical presentations are scoped to the venue and available work.'),
          ], 'A CREATIVE COLLABORATION', 'SPONSOR OPPORTUNITY'),
    copy('Audience & Releases', [('Mumbot’s artwork, products and Ghost Club community provide a starting audience for the browser world.', 'Mumbot’s products and Ghost Club community create a natural context for artist-led partnerships.'), ('Physical-product support; browser participation and repeat visits remain to be tested.', 'Existing product support. Future event attendance and partner reach remain to be measured.')]),
    copy('Live Experience'), sponsor_coffee, sponsor_formats, sponsor_package, sponsor_measure, sponsor_plan,
    team('CREATIVE DIRECTION AND WORLD PRODUCTION LED BY JADE KUEI AND CYRUS JAMES KHAN'),
    close('Let’s make<br/>something together', 'Plan a first collaboration around your audience and purpose.', 'Send the campaign goal, budget range and preferred window. We’ll develop a concept and a scoped proposal.'),
]
sponsor_appendix = [copy('Browser Prototype'), copy('World & Characters'), copy('Hub Possibilities')]

gallery_formats = rows('Exhibition Formats', 'A world at<br/>different scales',
    'Select a presentation format around the gallery’s architecture, program and technical capacity.', [
    ('Immersive<br/>projection', 'Present the forest at room scale using projection or LED displays, drawing on the Zerospace installation.', 'Adapt framing, playback and sound to the room. Equipment and installation are scoped with the venue.'),
    ('Screen-based<br/>installation', 'Create a focused encounter through a large screen or a dedicated viewing area, with space to pause.', 'Use a curated sequence or walkthrough of the existing world. Any visitor interaction is specified and tested.'),
    ('Across media', 'Place selected drawings, digital scenes and character objects in conversation with one another.', 'Confirm the available works, loans or editions with the artists. Labels connect the objects to the wider world.'),
    ], 'A browser companion is a possible later extension. The exhibition can be designed around existing visual work.', 'FORMATS FOR CURATORIAL DISCUSSION')

gallery_journey = new('Visitor Experience', 'v-split', '''
<figure class="v-art"><img src="assets/unreal-campfire-portrait.jpg" alt="Early Unreal scene with Mumbot characters around the campfire"/><figcaption>EARLY UNREAL WORLD · EXHIBITION REFERENCE</figcaption></figure>
<div><div class="eyebrow">A PROPOSED VISITOR JOURNEY</div><h2 class="mumbot">A place<br/>to pause</h2>
<div class="v-line"><h3>Enter the forest</h3><p>Light, sound and scale introduce the world before the visitor needs to understand its stories.</p></div>
<div class="v-line"><h3>Spend time with the characters</h3><p>Encounter the campfire and its inhabitants through a curated sequence or an agreed interactive format.</p></div>
<div class="v-line"><h3>Return to the artwork</h3><p>Drawings, objects and interpretation reveal how the world was made and offer another way to explore it.</p></div></div>''', 'PROPOSED EXHIBITION EXPERIENCE',
    note='Proposed exhibition visitor journey. Image is an existing early Unreal prototype scene. The exact media, interaction, duration and available physical works must be agreed for the venue.')

gallery_program = columns('Public Program', 'Around the<br/>exhibition',
    'A public program can make the relationship between character art, world-building and shared experience more visible.', [
    ('Artist conversation', 'A discussion with the creators about the characters, the forest and the move from drawings into a spatial world.', 'Format', 'A hosted conversation, in person or remote, subject to availability.'),
    ('Process workshop', 'A focused session on character drawing or on translating a visual world into lighting and digital space.', 'Format', 'A separately scoped workshop with an agreed audience, capacity and materials.'),
    ('Works &amp; editions', 'A viewing or release of available drawings, objects or editions associated with the exhibition.', 'Format', 'Selection, availability and any consignment terms agreed with the artists.'),
    ], 'Program fees, contributor availability, materials and any travel are confirmed in the exhibition proposal.', 'OPTIONAL PROGRAM ELEMENTS')

gallery_technical = new('Venue & Production', 'v-technical', head('Designed for<br/>the venue',
    'A site review turns the artistic proposal into a production plan and a practical technical rider.') + '''
<div class="v-two-columns"><div><h3>Artwork &amp; playback</h3>
<div class="v-line"><h3>Image and sound</h3><p>Agree display surfaces, resolution, audio approach and the effect of ambient light on the artwork.</p></div>
<div class="v-line"><h3>Playback and interaction</h3><p>Select the media and playback hardware. Test any controls, networking or visitor interaction in the agreed setup.</p></div>
<div class="v-line"><h3>Installation and support</h3><p>Define testing, startup and shutdown, staff handover and the support period.</p></div></div>
<div><h3>Space &amp; operations</h3>
<div class="v-line"><h3>The room</h3><p>Review dimensions, power, mounting, visitor flow and equipment access with the venue.</p></div>
<div class="v-line"><h3>Visitor comfort</h3><p>Plan seating, access routes, volume and interpretation. Provide alternatives where an interactive format needs them.</p></div>
<div class="v-line"><h3>Responsibilities</h3><p>Confirm who supplies equipment, installation labor, daily supervision and any network connection.</p></div></div></div>
<div class="v-footer">Final equipment and technical requirements follow the chosen format and site review.</div>''', 'TECHNICAL SCOPE TO BE AGREED')

gallery_commission = rows('Exhibition Partnership', 'An exhibition<br/>partnership',
    'Develop a proposal around the curatorial intention, available works and the practical scope of presentation.', [
    ('Curatorial<br/>scope', 'Agree the exhibition format, work selection, public program and proposed dates.', 'Begin with a conversation and a site review. Confirm which existing works and new adaptations are included.'),
    ('Budget &amp;<br/>production', 'Set an artist or exhibition fee and the budget for adaptation, installation and support.', 'Quote equipment, transport, travel and staffing separately where relevant. The venue’s budget guides the format.'),
    ('Presentation<br/>agreement', 'Agree the exhibition period, artwork credits, promotional image use and any edition sales.', 'Confirm responsibilities, rights and any consignment terms in the final proposal.'),
    ], '<strong>First step:</strong> share the curatorial focus, venue information, dates and budget range.', 'EXHIBITION PROPOSAL')

galleries = [
    cover('Gallery exhibition', 'An artist’s world, made spatial.', 'Installation &amp; public program', 'Exhibition proposal', 'Exhibitions'),
    intro('Curatorial Proposal', 'Enter a<br/>living forest',
          'Mumbot’s character universe becomes a shared setting for encounters with nature, memory and imagination.', [
          ('THE ARTISTIC IDEA', 'A forest inhabited by ghosts and nature spirits, where the campfire becomes a place to gather and pay attention.'),
          ('THE MATERIALS', 'Drawings, character objects and digital environments offer connected ways into the same world.'),
          ('THE PRESENTATION', 'An installation shaped around the gallery, with interpretation and a public program developed together.'),
          ], 'ARTWORK, WORLD-BUILDING AND SHARED SPACE', 'CURATORIAL PROPOSAL'),
    copy('Origin'), copy('World & Characters'), copy('Live Experience'), gallery_formats,
    gallery_journey, gallery_program, gallery_technical, gallery_commission,
    team('JADE KUEI: CHARACTER ART AND STORYTELLING · CYRUS JAMES KHAN: SPATIAL AND DIGITAL PRODUCTION'),
    close('Bring the forest<br/>into your space', 'Let’s develop an exhibition around your gallery and program.', 'Share the curatorial focus, floor plan, technical setup, dates and budget range to begin a tailored proposal.'),
]
gallery_appendix = [copy('Concepts'), copy('3D WIP'), copy('Browser Prototype')]


def roman(n):
    result = ''
    for value, symbol in [(10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]:
        while n >= value:
            result += symbol
            n -= value
    return result


def render(name, audience, main, appendix):
    slides, notes = [], []
    for index, (markup, note) in enumerate(main + appendix):
        label = html.unescape(re.search(r'data-label="([^"]+)"', markup)[1])
        if index >= len(main):
            tag = f'A{index-len(main)+1}'
            marker = f'APPENDIX {tag} · {label.upper()}'
            markup = re.sub(r'data-label="[^"]+"', f'data-label="{tag} · {html.escape(label)}" data-appendix="true"', markup, count=1)
        else:
            marker = f'{roman(index+1)} · {label.upper()}'
        markup = re.sub(r'(<div class="corner-mark tl mono">).*?(</div>)', lambda m:m[1]+html.escape(marker)+m[2], markup, count=1)
        if label == 'Closing':
            markup = markup.replace('MAIN PRESENTATION · 15 SLIDES', f'{audience.upper()} · {len(main)} MAIN SLIDES')
            markup = markup.replace('APPENDIX FOLLOWS · ARTWORK, PROTOTYPES &amp; PRODUCTION DETAILS', f'APPENDIX FOLLOWS · {len(appendix)} SUPPORTING SLIDES')
        slides.append(markup)
        notes.append(note)
    start = SOURCE.index('<deck-stage width=')
    end = SOURCE.index('</deck-stage>', start) + len('</deck-stage>')
    deck = '<deck-stage width="1920" height="1080" ambient-audio="assets/forestsound.WAV">\n\n'+'\n\n'.join(slides)+'\n\n</deck-stage>'
    output = SOURCE[:start]+deck+SOURCE[end:]
    output = re.sub(r'<script type="application/json" id="speaker-notes">[\s\S]*?</script>', lambda _: '<script type="application/json" id="speaker-notes">'+json.dumps(notes,ensure_ascii=False).replace('</','<\\/')+'</script>', output, count=1)
    output = output.replace('<title>Mumbot World Web · Pitch Deck</title>', f'<title>Mumbot World · {audience} Deck</title>')
    output = output.replace('</head>', '<link rel="stylesheet" href="deck-versions.css"/>\n</head>', 1)
    if 'notep' in output.lower():
        raise ValueError('Removed contributor returned to an edition')
    path = ROOT / f'{name}.html'
    path.write_text(output, encoding='utf-8', newline='\n')
    return {'file':path.name,'main_slides':len(main),'appendix_slides':len(appendix),'total':len(slides)}


if __name__ == '__main__':
    editions = [render('investors','Investor',investors,investor_appendix), render('sponsors','Sponsor',sponsors,sponsor_appendix), render('galleries','Gallery',galleries,gallery_appendix)]
    print(json.dumps(editions, indent=2))
