"""Allowlists and issue configuration for protectharvestcreek."""

CONCERNS = {
    "traffic": (
        "Traffic & Safety",
        "Increased traffic congestion, dangerous intersections, and pedestrian/cyclist safety risks",
    ),
    "density": (
        "Too Dense",
        "Excessive building density and height that is inappropriate for a low-density residential area",
    ),
    "parking": (
        "Parking",
        "Grossly inadequate parking provisions for the proposed number of units",
    ),
    "infrastructure": (
        "Infrastructure",
        "Strain on water, sewer, stormwater, and road infrastructure not built for this density",
    ),
    "schools": (
        "Schools",
        "Overcrowded schools and inadequate capacity for additional families",
    ),
    "character": (
        "Neighborhood Feel",
        "Loss of neighborhood character, livability, and sense of community",
    ),
    "environment": (
        "Environment",
        "Environmental impact, loss of green space, and disruption of wildlife corridors",
    ),
    "process": (
        "Public Process",
        "Insufficient public notice, rushed timeline, and lack of meaningful community input",
    ),
    "property-tax": (
        "Property Taxes",
        "Concern about rising property taxes and assessments driven by the development",
    ),
    "construction": (
        "Construction Impact",
        "Years of disruptive construction noise, dust, heavy trucks, and road closures",
    ),
    "precedent": (
        "Bad Precedent",
        "Setting a dangerous precedent for future high-density rezoning in residential neighborhoods",
    ),
}

# (emoji, chip_label, prompt_instruction)
VIBES = {
    "concerned": (
        "\U0001f3d8\ufe0f",
        "Concerned Neighbor",
        "Write as a concerned, polite, community-focused neighbor. Measured but clear.",
    ),
    "fired-up": (
        "\U0001f525",
        "Fired Up",
        "Write with passion and urgency. Be direct, forceful, and unapologetic.",
    ),
    "data-driven": (
        "\U0001f4ca",
        "Data & Facts",
        "Lead with facts, numbers, zoning code references, and infrastructure data.",
    ),
    "longtime": (
        "\U0001f3e1",
        "Long-time Resident",
        "Emphasize deep personal history, memories, and emotional connection to the neighborhood.",
    ),
    "parent": (
        "\U0001f468\u200d\U0001f467\u200d\U0001f466",
        "Worried Parent",
        "Focus on child safety, school walking routes, traffic near kids, and family quality of life.",
    ),
    "professional": (
        "\U0001f454",
        "Professional & Formal",
        "Write in a formal, measured, professional tone. Cite specific policy and code.",
    ),
    "heartfelt": (
        "\U0001f49b",
        "From the Heart",
        "Write an emotional, heartfelt appeal. Share what this neighborhood means personally.",
    ),
}

# (chip_label, prompt_instruction)
EXTRAS = {
    "meetings": (
        "I attend city meetings",
        "Mention that the resident regularly attends city commission meetings and is civically engaged",
    ),
    "property-values": (
        "Property values",
        "Express concern about negative impact on surrounding property values",
    ),
    "environmental-study": (
        "Request impact study",
        "Formally request a comprehensive environmental and traffic impact study before any vote",
    ),
    "hearing-extension": (
        "Extend public hearing",
        "Request an extension of the public comment period to allow more community input",
    ),
    "walk-bike": (
        "I walk/bike here",
        "Mention that the resident walks or bikes through this area regularly and has safety concerns",
    ),
    "kids-nearby": (
        "Kids go to school nearby",
        "Mention that their children attend a nearby school and use these roads daily",
    ),
    "taxpayer": (
        "Taxpayer concerns",
        "Raise concerns about the tax burden of supporting new infrastructure for this development",
    ),
    "senior": (
        "Senior/retiree",
        "Mention being a senior or retiree who chose this neighborhood for its quiet, low-density character",
    ),
}

RELATIONSHIPS = {
    "homeowner": ("\U0001f3e0", "Homeowner"),
    "renter": ("\U0001f511", "Renter"),
    "business": ("\U0001f3ea", "Nearby Business"),
    "commuter": ("\U0001f697", "I Commute Through"),
    "nearby": ("\U0001f4cd", "Live Nearby"),
}

YEARS_OPTIONS = {
    "new": ("< 1 year", "who recently moved to"),
    "1-5": ("1\u20135 years", "who has lived for a few years in"),
    "5-10": ("5\u201310 years", "who has lived for nearly a decade in"),
    "10-20": ("10\u201320 years", "who has lived for over a decade in"),
    "20+": ("20+ years", "who has lived for over twenty years in"),
}

TONES = {
    "formal": (
        "Very Formal",
        "Use formal language, full sentences, no contractions. Suitable for an official record.",
    ),
    "professional": (
        "Professional",
        "Professional but accessible. Clear and structured.",
    ),
    "conversational": (
        "Conversational",
        "Write like talking to a neighbor. Natural, warm, but still serious.",
    ),
    "passionate": (
        "Passionate",
        "Emotionally charged and urgent. This person cares deeply.",
    ),
}

ISSUES = {
    "annexation": {
        "email": "comments@bozeman.net",
        "subject": "Hanson Lane App 25775 Annexation and Zoning",
        "label": "Hanson Lane Annexation",
        "button": "Comment on Annexation (R-B Zoning)",
        "prompt_context": (
            "a proposed annexation and R-B rezoning of the Hanson Lane (Annie Street) parcel "
            "(Application 25775), directly adjacent to the Harvest Creek single-family neighborhood. "
            "R-B zoning allows mixed-use buildings up to 45 feet / 5 stories — textbook spot zoning "
            "into an area where surrounding properties are R-1/R-2 single-family homes at ≤6 units/acre. "
            "This sets a precedent for R-B zoning on ALL parcels along Fowler between Durston and Oak. "
            "R-A zoning (≤6 units/acre) matches the surrounding development pattern and satisfies the "
            "Community Plan's Urban Neighborhood designation without requiring R-B intensity. "
            "The area lacks transit and services that justify R-B — closest shopping is over a mile away. "
            "The annexation also extends Annie Street as a through street toward Emily Dickinson Elementary "
            "with no traffic calming, creating a safety hazard."
        ),
    },
    "housing": {
        "email": "comments@bozeman.net",
        "subject": "Public Comment on Fowler Avenue Housing Development",
        "label": "Fowler Housing Development",
        "button": "Comment on Fowler Housing",
        "prompt_context": (
            "the proposed Fowler Housing Development along Fowler Avenue from Oak Street to Annie Street, "
            "directly bordering 18 Harvest Creek homeowners' backyards. The City proposes up to 84 units "
            "at ~18 units/acre with 4-5 story buildings on a parcel only 150 feet wide — after setbacks "
            "and road right-of-way, only ~30 feet remains for structures. Unit prices of $450K–$650K are "
            "not affordable housing by any metric. Traffic from 168 cars would route through Farmall and "
            "Caterpillar Streets (residential roads not designed for this volume) with no access from "
            "Fowler Avenue itself. There is no roadway buffer between the development and existing backyards "
            "(unlike every other R-3 to R-1 transition in Bozeman). The City Commission agreed to a "
            "consensus-based engagement process with Harvest Creek HOA in January 2026 — separate zoning "
            "actions risk undermining that process. The city's 2017 purchase agreement committed to "
            "'preserve existing trees, open spaces and irrigation ditch.'"
        ),
    },
}
