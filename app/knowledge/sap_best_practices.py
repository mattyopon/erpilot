"""SAP Best Practices for S/4HANA - Scope Items Knowledge Base.

Based on SAP Best Practices for SAP S/4HANA (SAP Signavio Process Navigator).
Each Scope Item represents a standard business process configuration package
that SAP provides as part of the Fit-to-Standard methodology (SAP Activate).

Reference: https://help.sap.com/docs/SAP_BEST_PRACTICES
Reference: https://rapid.sap.com/bp/

Note on Scope Item IDs:
- IDs prefixed with letters (e.g., BD1, BF0, BMD) follow SAP's official
  Best Practices Explorer naming where known.
- IDs prefixed with "ERP-" are provisional identifiers assigned where the
  exact SAP Scope Item ID could not be confirmed from public documentation.
  These should be replaced with official IDs when verified.
"""

from __future__ import annotations

from typing import Any


# ============================================================================
# Data Structures
# ============================================================================

class ScopeItem:
    """Represents a single SAP Best Practices Scope Item."""

    __slots__ = (
        "scope_id", "name_en", "name_ja", "module", "category",
        "description", "key_transactions", "prerequisites",
        "industry_relevance", "process_steps", "common_gaps",
        "test_scenarios",
    )

    def __init__(
        self,
        scope_id: str,
        name_en: str,
        name_ja: str,
        module: str,
        category: str,
        description: str,
        key_transactions: list[str],
        prerequisites: list[str] | None = None,
        industry_relevance: list[str] | None = None,
        process_steps: list[str] | None = None,
        common_gaps: list[str] | None = None,
        test_scenarios: list[dict[str, Any]] | None = None,
    ) -> None:
        self.scope_id = scope_id
        self.name_en = name_en
        self.name_ja = name_ja
        self.module = module
        self.category = category
        self.description = description
        self.key_transactions = key_transactions
        self.prerequisites = prerequisites or []
        self.industry_relevance = industry_relevance or ["all"]
        self.process_steps = process_steps or []
        self.common_gaps = common_gaps or []
        self.test_scenarios = test_scenarios or []

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "scope_id": self.scope_id,
            "name_en": self.name_en,
            "name_ja": self.name_ja,
            "module": self.module,
            "category": self.category,
            "description": self.description,
            "key_transactions": self.key_transactions,
            "prerequisites": self.prerequisites,
            "industry_relevance": self.industry_relevance,
            "process_steps": self.process_steps,
            "common_gaps": self.common_gaps,
            "test_scenarios": self.test_scenarios,
        }


# ============================================================================
# Business Process Categories
# ============================================================================

PROCESS_CATEGORIES: dict[str, dict[str, str]] = {
    "O2C": {
        "name_en": "Order to Cash",
        "name_ja": "受注から入金",
        "description": "End-to-end sales process from order receipt to payment collection",
    },
    "P2P": {
        "name_en": "Procure to Pay",
        "name_ja": "購買から支払",
        "description": "End-to-end procurement process from requisition to payment",
    },
    "R2R": {
        "name_en": "Record to Report",
        "name_ja": "記帳から報告",
        "description": "Financial accounting and reporting processes",
    },
    "P2M": {
        "name_en": "Plan to Manufacture",
        "name_ja": "計画から製造",
        "description": "Production planning and manufacturing execution",
    },
    "WM": {
        "name_en": "Warehouse Management",
        "name_ja": "倉庫管理",
        "description": "Warehouse operations and inventory management",
    },
    "QM": {
        "name_en": "Quality Management",
        "name_ja": "品質管理",
        "description": "Quality inspection and control processes",
    },
    "AM": {
        "name_en": "Asset Management",
        "name_ja": "資産管理",
        "description": "Plant maintenance and asset lifecycle management",
    },
    "HCM": {
        "name_en": "Human Capital Management",
        "name_ja": "人的資本管理",
        "description": "HR processes from hire to retire",
    },
}


# ============================================================================
# Order to Cash (O2C) Scope Items
# ============================================================================

O2C_SCOPE_ITEMS: list[ScopeItem] = [
    ScopeItem(
        scope_id="BD1",
        name_en="Sales Order Processing",
        name_ja="受注処理",
        module="SD",
        category="O2C",
        description="Standard sales order creation, change, and processing including "
                    "availability check, pricing, and partner determination.",
        key_transactions=["VA01", "VA02", "VA03", "VA05"],
        prerequisites=[],
        industry_relevance=["all"],
        process_steps=[
            "Create sales order (VA01)",
            "System performs availability check (ATP)",
            "Pricing determined via condition technique",
            "Partner functions determined automatically",
            "Order confirmation output generated",
            "Delivery scheduling calculated",
        ],
        common_gaps=[
            "Complex multi-level pricing not covered by standard condition technique",
            "Custom order types beyond standard OR/SO",
            "Non-standard availability check logic (e.g., project-based ATP)",
            "Custom document flow requirements",
            "Integration with external product configurators",
        ],
        test_scenarios=[
            {"name": "Standard Order Creation", "name_ja": "標準受注登録",
             "steps": [
                 {"t_code": "VA01", "action": "Create standard order type OR",
                  "input": "Sales org, Customer, Material, Qty",
                  "expected": "Order created with pricing and ATP check"},
             ]},
            {"name": "Order with Availability Check", "name_ja": "在庫引当チェック付き受注",
             "steps": [
                 {"t_code": "VA01", "action": "Create order for material with limited stock",
                  "input": "Material with partial availability",
                  "expected": "Partial confirmation with delivery proposal"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="BD3",
        name_en="Sales Quotation Processing",
        name_ja="見積処理",
        module="SD",
        category="O2C",
        description="Creation and management of sales quotations with validity periods, "
                    "follow-up to sales orders, and quotation tracking.",
        key_transactions=["VA21", "VA22", "VA23", "VA25"],
        prerequisites=[],
        industry_relevance=["all"],
        process_steps=[
            "Create quotation (VA21)",
            "Define validity period",
            "Pricing and conditions maintained",
            "Send quotation to customer",
            "Monitor quotation status (VA25)",
            "Convert quotation to sales order",
        ],
        common_gaps=[
            "Complex quotation approval workflows",
            "Quotation versioning and comparison",
            "Integration with external CPQ (Configure-Price-Quote) tools",
            "Custom quotation validity rules per customer segment",
        ],
        test_scenarios=[
            {"name": "Quotation to Order", "name_ja": "見積から受注への変換",
             "steps": [
                 {"t_code": "VA21", "action": "Create quotation",
                  "input": "Customer, Material, Qty, Validity dates",
                  "expected": "Quotation created"},
                 {"t_code": "VA01", "action": "Create order with reference to quotation",
                  "input": "Reference quotation number",
                  "expected": "Order created with quotation reference"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="BD5",
        name_en="Credit Management",
        name_ja="与信管理",
        module="SD",
        category="O2C",
        description="SAP Credit Management for automatic credit limit checks during "
                    "sales order processing, delivery, and goods issue.",
        key_transactions=["UKM_BP", "FD32", "UKM_COLL"],
        prerequisites=["BD1"],
        industry_relevance=["all"],
        process_steps=[
            "Maintain credit master data (UKM_BP)",
            "Set credit limit and risk category",
            "Automatic credit check during order processing",
            "Credit block handling and release",
            "Credit exposure monitoring",
        ],
        common_gaps=[
            "External credit rating agency integration",
            "Dynamic credit limit adjustment based on payment behavior",
            "Group-level credit management across company codes",
            "Custom credit scoring models",
        ],
        test_scenarios=[
            {"name": "Credit Check Block and Release", "name_ja": "与信チェックブロック・解除",
             "steps": [
                 {"t_code": "VA01", "action": "Create order exceeding credit limit",
                  "input": "Customer with low credit limit, high-value order",
                  "expected": "Order blocked for credit"},
                 {"t_code": "UKM_COLL", "action": "Release credit block",
                  "input": "Blocked order number",
                  "expected": "Order released for processing"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="BDJ",
        name_en="Advanced Credit Management",
        name_ja="高度与信管理",
        module="SD",
        category="O2C",
        description="Extended credit management with credit rules engine, "
                    "credit score calculation, and collection management.",
        key_transactions=["UKM_BP", "UKM_COLL", "UKM_SCORE"],
        prerequisites=["BD5"],
        industry_relevance=["all"],
        process_steps=[
            "Configure credit rules engine",
            "Define credit scoring formula",
            "Automatic credit limit recalculation",
            "Collection strategy assignment",
            "Dispute management integration",
        ],
        common_gaps=[
            "Machine learning-based credit scoring",
            "Real-time external credit data feeds",
            "Complex group credit hierarchies",
        ],
        test_scenarios=[
            {"name": "Credit Score Recalculation", "name_ja": "与信スコア再計算",
             "steps": [
                 {"t_code": "UKM_SCORE", "action": "Trigger score recalculation",
                  "input": "Customer with changed payment history",
                  "expected": "Credit score updated, limit adjusted"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="BD7",
        name_en="Free-of-Charge Delivery",
        name_ja="無償出荷",
        module="SD",
        category="O2C",
        description="Processing of free-of-charge deliveries including samples, "
                    "replacements, and promotional goods.",
        key_transactions=["VA01", "VL01N"],
        prerequisites=["BD1"],
        industry_relevance=["manufacturing", "retail"],
        process_steps=[
            "Create free-of-charge order (order type FD)",
            "Pricing set to zero",
            "Delivery processing",
            "Goods issue without billing",
        ],
        common_gaps=[
            "Complex approval workflows for free goods",
            "Budget control for free-of-charge deliveries",
            "Reporting on free goods by reason code",
        ],
        test_scenarios=[
            {"name": "Free-of-Charge Delivery", "name_ja": "無償出荷処理",
             "steps": [
                 {"t_code": "VA01", "action": "Create order type FD",
                  "input": "Customer, Material, Qty, Order type FD",
                  "expected": "Order created with zero pricing"},
                 {"t_code": "VL01N", "action": "Create delivery",
                  "input": "Reference order",
                  "expected": "Delivery created, no billing reference"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="BD9",
        name_en="Returns and Complaints Processing",
        name_ja="返品・クレーム処理",
        module="SD",
        category="O2C",
        description="Customer returns processing including return order creation, "
                    "goods receipt, inspection, and credit memo generation.",
        key_transactions=["VA01", "VL01N", "VF01"],
        prerequisites=["BD1"],
        industry_relevance=["all"],
        process_steps=[
            "Create returns order (order type RE)",
            "Create return delivery",
            "Post goods receipt for return",
            "Quality inspection (optional)",
            "Create credit memo",
        ],
        common_gaps=[
            "Complex return reason code analysis",
            "Partial return with restocking fees",
            "Cross-border return logistics",
            "Automated return authorization (RMA) process",
        ],
        test_scenarios=[
            {"name": "Full Return Process", "name_ja": "返品処理フルプロセス",
             "steps": [
                 {"t_code": "VA01", "action": "Create return order",
                  "input": "Order type RE, Reference original order",
                  "expected": "Return order created"},
                 {"t_code": "VL01N", "action": "Create return delivery",
                  "input": "Reference return order",
                  "expected": "Return delivery created"},
                 {"t_code": "VF01", "action": "Create credit memo",
                  "input": "Reference return order",
                  "expected": "Credit memo posted to FI"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="BDH",
        name_en="Third-Party Order Processing",
        name_ja="直送処理",
        module="SD",
        category="O2C",
        description="Drop shipment processing where vendor ships directly to customer. "
                    "Sales order triggers purchase order to vendor.",
        key_transactions=["VA01", "ME21N", "MIRO", "VF01"],
        prerequisites=["BD1", "BMD"],
        industry_relevance=["manufacturing", "retail", "wholesale"],
        process_steps=[
            "Create third-party sales order (item category TAS)",
            "Automatic purchase requisition created",
            "Convert PR to purchase order",
            "Vendor ships to customer",
            "Invoice receipt from vendor",
            "Billing to customer",
        ],
        common_gaps=[
            "Tracking shipment status from vendor to customer",
            "Split deliveries across multiple vendors",
            "Custom margin calculation for third-party items",
            "Serial number tracking through third-party chain",
        ],
        test_scenarios=[
            {"name": "Third-Party Order to Billing", "name_ja": "直送 受注から請求",
             "steps": [
                 {"t_code": "VA01", "action": "Create third-party order",
                  "input": "Item category TAS, Customer, Material, Vendor",
                  "expected": "Order created, PR auto-generated"},
                 {"t_code": "ME21N", "action": "Create PO from PR",
                  "input": "Purchase requisition reference",
                  "expected": "PO created to vendor"},
                 {"t_code": "VF01", "action": "Bill customer",
                  "input": "Reference sales order",
                  "expected": "Invoice posted"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="BKP",
        name_en="Intercompany Sales Processing",
        name_ja="会社間販売処理",
        module="SD",
        category="O2C",
        description="Sales between affiliated companies. Selling company creates "
                    "order, supplying company fulfills and creates intercompany billing.",
        key_transactions=["VA01", "VL01N", "VF01", "VF11"],
        prerequisites=["BD1"],
        industry_relevance=["all"],
        process_steps=[
            "Create intercompany sales order",
            "Delivery from supplying plant",
            "Intercompany billing (supplying company)",
            "Customer billing (selling company)",
            "Intercompany reconciliation",
        ],
        common_gaps=[
            "Transfer pricing adjustments",
            "Multi-currency intercompany settlements",
            "Complex intercompany profit elimination",
            "Intercompany stock transfer vs. sales distinction",
        ],
        test_scenarios=[
            {"name": "Intercompany Sales", "name_ja": "会社間販売処理",
             "steps": [
                 {"t_code": "VA01", "action": "Create intercompany order",
                  "input": "Selling company order, Supplying plant",
                  "expected": "Order created with intercompany data"},
                 {"t_code": "VF01", "action": "Create intercompany invoice",
                  "input": "Delivery from supplying company",
                  "expected": "Intercompany invoice posted"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="J58",
        name_en="Revenue Recognition",
        name_ja="収益認識",
        module="SD",
        category="O2C",
        description="Revenue recognition based on IFRS 15 / ASC 606 standards. "
                    "Supports event-based and time-based revenue recognition.",
        key_transactions=["VF01", "FARR_MAINTAIN"],
        prerequisites=["BD1", "BF0"],
        industry_relevance=["all"],
        process_steps=[
            "Define revenue recognition contracts",
            "Identify performance obligations",
            "Allocate transaction price",
            "Recognize revenue upon satisfaction of obligations",
            "Revenue recognition reporting",
        ],
        common_gaps=[
            "Complex multi-element arrangements",
            "Variable consideration estimation",
            "Contract modification handling",
            "Retrospective vs. prospective adjustment",
        ],
        test_scenarios=[
            {"name": "Event-Based Revenue Recognition", "name_ja": "イベントベース収益認識",
             "steps": [
                 {"t_code": "VF01", "action": "Create invoice triggering revenue event",
                  "input": "Billing document with revenue recognition",
                  "expected": "Revenue recognized per IFRS 15 rules"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="ERP-O2C-010",
        name_en="Delivery Processing and Shipping",
        name_ja="出荷・配送処理",
        module="SD",
        category="O2C",
        description="Outbound delivery processing including picking, packing, "
                    "goods issue, and shipment creation. Covers shipping point "
                    "and route determination.",
        key_transactions=["VL01N", "VL02N", "VL03N", "VT01N"],
        prerequisites=["BD1"],
        industry_relevance=["all"],
        process_steps=[
            "Create outbound delivery (VL01N)",
            "Picking (warehouse task or manual)",
            "Packing (HU management)",
            "Post goods issue (VL02N)",
            "Create shipment (optional, VT01N)",
            "Output: Delivery note, shipping labels",
        ],
        common_gaps=[
            "Complex wave-based picking strategies",
            "Multi-stop shipping and route optimization",
            "Custom packing rules and handling unit hierarchies",
            "Integration with external TMS (Transportation Management System)",
        ],
        test_scenarios=[
            {"name": "Delivery to Goods Issue", "name_ja": "出荷から出庫転記",
             "steps": [
                 {"t_code": "VL01N", "action": "Create delivery from order",
                  "input": "Sales order reference",
                  "expected": "Delivery created"},
                 {"t_code": "VL02N", "action": "Pick and post goods issue",
                  "input": "Delivery number, picking confirmation",
                  "expected": "Goods issue posted, inventory reduced"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="ERP-O2C-011",
        name_en="Billing and Invoicing",
        name_ja="請求処理",
        module="SD",
        category="O2C",
        description="Billing document creation including invoices, credit memos, "
                    "debit memos, and pro-forma invoices. Includes billing plans "
                    "for periodic and milestone billing.",
        key_transactions=["VF01", "VF02", "VF03", "VF04"],
        prerequisites=["BD1"],
        industry_relevance=["all"],
        process_steps=[
            "Create billing document (VF01)",
            "Billing type determination",
            "Pricing carried from order/delivery",
            "Tax calculation",
            "FI document posting (automatic)",
            "Output: Invoice print/EDI",
        ],
        common_gaps=[
            "Complex billing split rules beyond standard",
            "Consolidated billing across orders/deliveries",
            "E-invoicing compliance (country-specific)",
            "Self-billing / pay-on-receipt processes",
        ],
        test_scenarios=[
            {"name": "Standard Billing", "name_ja": "標準請求処理",
             "steps": [
                 {"t_code": "VF01", "action": "Create invoice from delivery",
                  "input": "Delivery number",
                  "expected": "Invoice created, FI document generated"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="ERP-O2C-012",
        name_en="Rebate Processing",
        name_ja="リベート処理",
        module="SD",
        category="O2C",
        description="Volume-based rebate agreements with customers including "
                    "accrual posting and periodic settlement.",
        key_transactions=["VB01", "VB02", "VB03", "VBO1"],
        prerequisites=["BD1", "BF0"],
        industry_relevance=["manufacturing", "retail", "wholesale"],
        process_steps=[
            "Create rebate agreement (VB01)",
            "Define condition records and scales",
            "Automatic accrual posting during billing",
            "Periodic rebate settlement",
            "Credit memo creation",
        ],
        common_gaps=[
            "Complex multi-tier rebate calculations",
            "Rebate agreements spanning multiple fiscal years",
            "Retroactive rebate adjustments",
            "Integration with trade promotion management",
        ],
        test_scenarios=[
            {"name": "Rebate Agreement Settlement", "name_ja": "リベート契約決済",
             "steps": [
                 {"t_code": "VB01", "action": "Create rebate agreement",
                  "input": "Customer, Condition type, Scale",
                  "expected": "Rebate agreement created"},
                 {"t_code": "VBO1", "action": "Settle rebate",
                  "input": "Agreement number, Settlement period",
                  "expected": "Credit memo generated"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="ERP-O2C-013",
        name_en="Consignment Processing",
        name_ja="委託販売処理",
        module="SD",
        category="O2C",
        description="Consignment stock at customer location including fill-up, "
                    "issue, pickup, and returns of consignment stock.",
        key_transactions=["VA01", "VL01N"],
        prerequisites=["BD1"],
        industry_relevance=["manufacturing", "retail"],
        process_steps=[
            "Consignment fill-up (CF order type)",
            "Consignment issue (CI order type)",
            "Consignment pickup (CP order type)",
            "Consignment return (CR order type)",
            "Billing upon consignment issue",
        ],
        common_gaps=[
            "Complex consignment stock valuation",
            "Multi-location consignment tracking",
            "Consignment stock aging and rotation",
            "Automatic replenishment of consignment stock",
        ],
        test_scenarios=[
            {"name": "Consignment Fill-up and Issue", "name_ja": "委託在庫補充・消費",
             "steps": [
                 {"t_code": "VA01", "action": "Create consignment fill-up order",
                  "input": "Order type CF, Customer, Material, Qty",
                  "expected": "Consignment stock transferred to customer"},
                 {"t_code": "VA01", "action": "Create consignment issue",
                  "input": "Order type CI, Customer, Material, Qty",
                  "expected": "Billing triggered for consumed stock"},
             ]},
        ],
    ),
]


# ============================================================================
# Procure to Pay (P2P) Scope Items
# ============================================================================

P2P_SCOPE_ITEMS: list[ScopeItem] = [
    ScopeItem(
        scope_id="BMD",
        name_en="Purchase Order Processing",
        name_ja="発注処理",
        module="MM",
        category="P2P",
        description="End-to-end purchase order creation and processing including "
                    "source determination, pricing, and approval workflows.",
        key_transactions=["ME21N", "ME22N", "ME23N", "ME28", "ME2M"],
        prerequisites=[],
        industry_relevance=["all"],
        process_steps=[
            "Create purchase requisition (ME51N) or direct PO",
            "Source determination (info record, contract, source list)",
            "Purchase order creation (ME21N)",
            "Release/approval strategy execution",
            "PO output (print/EDI)",
            "PO monitoring (ME2M)",
        ],
        common_gaps=[
            "Complex multi-level approval workflows beyond standard release strategy",
            "Automatic supplier selection based on custom scoring",
            "PO collaboration portal for suppliers",
            "Advanced commitment management",
        ],
        test_scenarios=[
            {"name": "PO with Release Strategy", "name_ja": "承認付き発注処理",
             "steps": [
                 {"t_code": "ME21N", "action": "Create purchase order",
                  "input": "Vendor, Material, Qty, Price",
                  "expected": "PO created, pending release"},
                 {"t_code": "ME28", "action": "Release purchase order",
                  "input": "PO number, Release code",
                  "expected": "PO released for processing"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="BMP",
        name_en="Subcontracting",
        name_ja="外注加工",
        module="MM",
        category="P2P",
        description="Subcontracting process where components are provided to "
                    "vendor for processing. Includes component provision tracking.",
        key_transactions=["ME21N", "MIGO", "ME2O"],
        prerequisites=["BMD"],
        industry_relevance=["manufacturing"],
        process_steps=[
            "Create subcontracting PO (item category L)",
            "Provide components to subcontractor",
            "Monitor subcontractor stock (ME2O)",
            "Goods receipt of finished product",
            "Invoice verification",
        ],
        common_gaps=[
            "Complex BOM management for subcontracting",
            "Multiple subcontractor tiers",
            "Scrap reporting from subcontractor",
            "Quality inspection at subcontractor site",
        ],
        test_scenarios=[
            {"name": "Subcontracting Process", "name_ja": "外注加工プロセス",
             "steps": [
                 {"t_code": "ME21N", "action": "Create subcontracting PO",
                  "input": "Item category L, Material, Components",
                  "expected": "Subcontracting PO with component list"},
                 {"t_code": "MIGO", "action": "Goods receipt of finished product",
                  "input": "PO reference, Mvt type 101",
                  "expected": "Finished product received, components consumed"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="BMR",
        name_en="Service Procurement",
        name_ja="サービス調達",
        module="MM",
        category="P2P",
        description="Procurement of services using service entry sheets including "
                    "service specifications, acceptance, and invoice verification.",
        key_transactions=["ME21N", "ML81N", "MIRO"],
        prerequisites=["BMD"],
        industry_relevance=["all"],
        process_steps=[
            "Create service PO with service specifications",
            "Service entry sheet creation (ML81N)",
            "Service acceptance/approval",
            "Invoice verification against service entry",
        ],
        common_gaps=[
            "Complex time-and-material billing",
            "Service-level agreement (SLA) monitoring",
            "Blanket service PO with flexible limits",
            "Multi-phase service acceptance workflows",
        ],
        test_scenarios=[
            {"name": "Service PO to Invoice", "name_ja": "サービス発注から請求",
             "steps": [
                 {"t_code": "ME21N", "action": "Create service PO",
                  "input": "Account assignment, Service lines",
                  "expected": "Service PO created"},
                 {"t_code": "ML81N", "action": "Create service entry sheet",
                  "input": "PO reference, Service quantities",
                  "expected": "Entry sheet created and accepted"},
                 {"t_code": "MIRO", "action": "Invoice verification",
                  "input": "PO reference, Invoice amount",
                  "expected": "Invoice matched to entry sheet"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="BNB",
        name_en="Evaluated Receipt Settlement (ERS)",
        name_ja="自動検収決済",
        module="MM",
        category="P2P",
        description="Automatic invoice generation based on goods receipt, "
                    "eliminating the need for vendor invoice processing.",
        key_transactions=["MRRL", "MIRO"],
        prerequisites=["BMD"],
        industry_relevance=["manufacturing", "retail"],
        process_steps=[
            "Configure vendor for ERS",
            "Goods receipt posted",
            "Run ERS program (MRRL)",
            "Automatic invoice document created",
            "Payment processing",
        ],
        common_gaps=[
            "Partial ERS (some items standard, some ERS)",
            "Price variance handling in ERS",
            "ERS with consignment stock",
            "Tax handling in auto-generated invoices",
        ],
        test_scenarios=[
            {"name": "ERS Processing", "name_ja": "自動検収決済処理",
             "steps": [
                 {"t_code": "MIGO", "action": "Post goods receipt",
                  "input": "PO reference with ERS flag",
                  "expected": "GR posted"},
                 {"t_code": "MRRL", "action": "Run ERS",
                  "input": "Vendor, Company code, Date range",
                  "expected": "Invoice auto-generated from GR"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="BNX",
        name_en="Supplier Invoice Processing",
        name_ja="仕入先請求書処理",
        module="MM",
        category="P2P",
        description="Logistics invoice verification including 3-way matching "
                    "(PO, GR, Invoice), tolerance checks, and blocking.",
        key_transactions=["MIRO", "MIR4", "MRBR"],
        prerequisites=["BMD"],
        industry_relevance=["all"],
        process_steps=[
            "Enter vendor invoice (MIRO)",
            "Automatic 3-way match (PO, GR, Invoice)",
            "Tolerance check",
            "Blocking/releasing blocked invoices",
            "FI document posting",
        ],
        common_gaps=[
            "OCR/AI-based invoice capture and auto-matching",
            "Complex tolerance rules by vendor/material group",
            "Multi-PO invoice matching",
            "Credit memo and subsequent debit processing",
        ],
        test_scenarios=[
            {"name": "3-Way Match Invoice", "name_ja": "3点照合請求書処理",
             "steps": [
                 {"t_code": "MIRO", "action": "Enter vendor invoice",
                  "input": "PO reference, Invoice amount, Tax code",
                  "expected": "Invoice posted with 3-way match"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="J44",
        name_en="Central Procurement",
        name_ja="中央購買",
        module="MM",
        category="P2P",
        description="Centralized procurement hub for managing purchasing across "
                    "multiple company codes and plants.",
        key_transactions=["ME21N", "ME51N", "ME59N"],
        prerequisites=["BMD"],
        industry_relevance=["all"],
        process_steps=[
            "Central requisition pooling",
            "Cross-company code purchase order creation",
            "Centralized contract management",
            "Consolidated supplier negotiations",
        ],
        common_gaps=[
            "Complex organizational mapping for central procurement",
            "Different tax and legal requirements per company code",
            "Shared service center cost allocation",
            "Cross-border procurement compliance",
        ],
        test_scenarios=[
            {"name": "Cross-Company Procurement", "name_ja": "会社間集中購買",
             "steps": [
                 {"t_code": "ME21N", "action": "Create cross-company PO",
                  "input": "Central purchasing org, Multiple plants",
                  "expected": "PO created serving multiple entities"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="ERP-P2P-007",
        name_en="Purchase Requisition Processing",
        name_ja="購買依頼処理",
        module="MM",
        category="P2P",
        description="Purchase requisition creation, approval, and conversion to "
                    "purchase orders including MRP-generated requisitions.",
        key_transactions=["ME51N", "ME52N", "ME53N", "ME54N", "ME57"],
        prerequisites=[],
        industry_relevance=["all"],
        process_steps=[
            "Create purchase requisition (ME51N)",
            "Release/approval of PR",
            "Assign source of supply (ME57)",
            "Convert PR to PO (ME59N)",
        ],
        common_gaps=[
            "Self-service requisitioning portal for end users",
            "Catalog-based ordering integration",
            "Complex approval matrix (amount + org unit + material group)",
            "Free-text item requisitions with complex routing",
        ],
        test_scenarios=[
            {"name": "PR to PO Conversion", "name_ja": "購買依頼から発注変換",
             "steps": [
                 {"t_code": "ME51N", "action": "Create purchase requisition",
                  "input": "Material, Qty, Delivery date, Plant",
                  "expected": "PR created"},
                 {"t_code": "ME21N", "action": "Create PO from PR",
                  "input": "PR reference",
                  "expected": "PO created with PR reference"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="ERP-P2P-008",
        name_en="Goods Receipt Processing",
        name_ja="入庫処理",
        module="MM",
        category="P2P",
        description="Goods receipt against purchase orders, production orders, "
                    "and other sources including quality inspection integration.",
        key_transactions=["MIGO"],
        prerequisites=["BMD"],
        industry_relevance=["all"],
        process_steps=[
            "Goods receipt against PO (MIGO, Mvt type 101)",
            "Automatic quality inspection trigger (if configured)",
            "Stock posting to unrestricted or inspection stock",
            "Automatic FI document creation",
            "GR/IR clearing account posting",
        ],
        common_gaps=[
            "Complex receiving inspection workflows",
            "Mobile-based goods receipt (barcode/RF scanning)",
            "Automatic putaway to warehouse management",
            "Goods receipt with serial number and batch creation",
        ],
        test_scenarios=[
            {"name": "GR against PO", "name_ja": "発注参照入庫",
             "steps": [
                 {"t_code": "MIGO", "action": "Post goods receipt",
                  "input": "PO reference, Mvt type 101, Qty",
                  "expected": "GR posted, stock increased, FI doc created"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="ERP-P2P-009",
        name_en="Contract and Scheduling Agreement Management",
        name_ja="基本契約・分納契約管理",
        module="MM",
        category="P2P",
        description="Long-term purchasing agreements including quantity contracts, "
                    "value contracts, and scheduling agreements with delivery schedules.",
        key_transactions=["ME31K", "ME31L", "ME35K", "ME35L", "ME38"],
        prerequisites=[],
        industry_relevance=["manufacturing", "retail"],
        process_steps=[
            "Create contract (ME31K/ME31L)",
            "Release against contract",
            "Scheduling agreement delivery schedules (ME38)",
            "Contract monitoring and expiry management",
        ],
        common_gaps=[
            "Complex contract pricing with escalation clauses",
            "Multi-year contract rollover with price adjustments",
            "Contract compliance monitoring and penalty calculation",
            "Blanket contract with flexible allocation",
        ],
        test_scenarios=[
            {"name": "Contract Release Order", "name_ja": "基本契約リリース発注",
             "steps": [
                 {"t_code": "ME31K", "action": "Create quantity contract",
                  "input": "Vendor, Material, Target qty, Validity",
                  "expected": "Contract created"},
                 {"t_code": "ME21N", "action": "Create release order against contract",
                  "input": "Contract reference, Qty",
                  "expected": "PO created with contract reference"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="ERP-P2P-010",
        name_en="Vendor Evaluation",
        name_ja="仕入先評価",
        module="MM",
        category="P2P",
        description="Automatic vendor scoring based on quality, price, delivery "
                    "performance, and service criteria.",
        key_transactions=["ME61", "ME62", "ME63", "ME6B"],
        prerequisites=["BMD"],
        industry_relevance=["all"],
        process_steps=[
            "Define evaluation criteria and weighting",
            "Automatic score calculation from GR/QM/Invoice data",
            "Manual score input for subjective criteria",
            "Vendor ranking and comparison",
        ],
        common_gaps=[
            "Custom evaluation criteria beyond standard 4 main criteria",
            "Supplier risk assessment integration",
            "Vendor development program tracking",
            "Dynamic weighting adjustments by commodity",
        ],
        test_scenarios=[
            {"name": "Vendor Score Review", "name_ja": "仕入先スコア確認",
             "steps": [
                 {"t_code": "ME61", "action": "Maintain vendor evaluation",
                  "input": "Vendor, Purchasing org",
                  "expected": "Evaluation scores displayed and maintained"},
             ]},
        ],
    ),
]


# ============================================================================
# Record to Report (R2R) Scope Items
# ============================================================================

R2R_SCOPE_ITEMS: list[ScopeItem] = [
    ScopeItem(
        scope_id="BF0",
        name_en="General Ledger Accounting",
        name_ja="総勘定元帳会計",
        module="FI",
        category="R2R",
        description="Universal Journal-based GL accounting including journal entries, "
                    "document management, and real-time financial reporting.",
        key_transactions=["FB50", "FB01", "FB03", "FAGLB03"],
        prerequisites=[],
        industry_relevance=["all"],
        process_steps=[
            "Chart of accounts configuration",
            "GL account master data maintenance",
            "Journal entry posting (FB50/FB01)",
            "Document display and line item reports",
            "Trial balance and financial statement reporting",
        ],
        common_gaps=[
            "Parallel accounting (multiple GAAP) beyond standard 2 ledgers",
            "Complex allocation journal entries with dynamic rules",
            "Custom financial statement versions",
            "GL account derivation rules beyond standard substitution",
        ],
        test_scenarios=[
            {"name": "GL Journal Entry", "name_ja": "仕訳伝票転記",
             "steps": [
                 {"t_code": "FB50", "action": "Post journal entry",
                  "input": "Company code, Debit/Credit accounts, Amount",
                  "expected": "FI document posted and balanced"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="BF2",
        name_en="Accounts Payable",
        name_ja="買掛金管理",
        module="FI",
        category="R2R",
        description="Vendor invoice management, payment processing, and AP aging "
                    "including automatic payment program.",
        key_transactions=["FB60", "F110", "FBL1N", "F-53"],
        prerequisites=["BF0"],
        industry_relevance=["all"],
        process_steps=[
            "Vendor master data maintenance",
            "Invoice posting (FB60)",
            "Payment block and release management",
            "Automatic payment program (F110)",
            "Payment media generation (check, bank transfer)",
            "AP aging analysis",
        ],
        common_gaps=[
            "Complex payment method selection logic",
            "Cross-company payment processing",
            "Payment factory/in-house bank integration",
            "Dynamic discounting with supplier financing",
        ],
        test_scenarios=[
            {"name": "AP Invoice to Payment", "name_ja": "買掛金請求から支払",
             "steps": [
                 {"t_code": "FB60", "action": "Post vendor invoice",
                  "input": "Vendor, Amount, GL account, Tax code",
                  "expected": "AP document posted"},
                 {"t_code": "F110", "action": "Run payment program",
                  "input": "Run date, Company code, Payment method",
                  "expected": "Payment executed, AP cleared"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="BF4",
        name_en="Accounts Receivable",
        name_ja="売掛金管理",
        module="FI",
        category="R2R",
        description="Customer invoice management, incoming payment processing, "
                    "dunning, and AR aging analysis.",
        key_transactions=["FB70", "F-28", "F-32", "F150", "FBL5N"],
        prerequisites=["BF0"],
        industry_relevance=["all"],
        process_steps=[
            "Customer master data maintenance",
            "Invoice posting (FB70) or from SD billing",
            "Incoming payment processing (F-28)",
            "Automatic clearing (F-32)",
            "Dunning program execution (F150)",
            "AR aging analysis",
        ],
        common_gaps=[
            "Complex payment matching rules for high-volume payments",
            "Lockbox processing customization",
            "Dispute management integration",
            "Revenue-based credit memo processing",
        ],
        test_scenarios=[
            {"name": "AR Invoice to Collection", "name_ja": "売掛金請求から入金",
             "steps": [
                 {"t_code": "FB70", "action": "Post customer invoice",
                  "input": "Customer, Amount, GL account",
                  "expected": "AR document posted"},
                 {"t_code": "F-28", "action": "Post incoming payment",
                  "input": "Customer, Amount, Invoice reference",
                  "expected": "Payment posted, invoice cleared"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="BF6",
        name_en="Fixed Asset Accounting",
        name_ja="固定資産会計",
        module="FI",
        category="R2R",
        description="Asset lifecycle management including acquisition, depreciation, "
                    "transfer, and retirement.",
        key_transactions=["AS01", "ABZON", "AFAB", "ABAVN", "ABUMN"],
        prerequisites=["BF0"],
        industry_relevance=["all"],
        process_steps=[
            "Asset master data creation (AS01)",
            "Asset acquisition posting (ABZON/F-90)",
            "Periodic depreciation run (AFAB)",
            "Asset transfer between cost centers (ABUMN)",
            "Asset retirement/scrapping (ABAVN)",
            "Asset reporting and reconciliation",
        ],
        common_gaps=[
            "Complex depreciation methods (units of production, etc.)",
            "Asset under construction (AuC) with settlement rules",
            "Lease accounting (IFRS 16) integration",
            "Mass asset creation and changes",
        ],
        test_scenarios=[
            {"name": "Asset Lifecycle", "name_ja": "固定資産ライフサイクル",
             "steps": [
                 {"t_code": "AS01", "action": "Create asset master",
                  "input": "Asset class, Cost center, Description",
                  "expected": "Asset master created"},
                 {"t_code": "ABZON", "action": "Post asset acquisition",
                  "input": "Asset number, Amount, Vendor (optional)",
                  "expected": "Acquisition posted to asset and GL"},
                 {"t_code": "AFAB", "action": "Run depreciation",
                  "input": "Company code, Fiscal year, Period",
                  "expected": "Depreciation posted"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="BFB",
        name_en="Bank Account Management",
        name_ja="銀行口座管理",
        module="FI",
        category="R2R",
        description="Bank master data management, electronic bank statement "
                    "processing, and bank reconciliation.",
        key_transactions=["FI01", "FF67", "FEBAN", "FF_5"],
        prerequisites=["BF0"],
        industry_relevance=["all"],
        process_steps=[
            "Bank master data maintenance",
            "Electronic bank statement import",
            "Automatic bank statement posting (FEBAN)",
            "Manual bank reconciliation",
            "Cash position monitoring",
        ],
        common_gaps=[
            "Multi-bank connectivity with different formats (MT940, BAI2, CAMT)",
            "Advanced cash pooling structures",
            "In-house bank and payment factory",
            "Real-time bank balance monitoring",
        ],
        test_scenarios=[
            {"name": "Bank Statement Processing", "name_ja": "銀行明細処理",
             "steps": [
                 {"t_code": "FEBAN", "action": "Import and post bank statement",
                  "input": "Bank statement file",
                  "expected": "Statement items matched and posted"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="BGE",
        name_en="Financial Close",
        name_ja="財務決算処理",
        module="FI",
        category="R2R",
        description="Period-end and year-end closing activities including "
                    "foreign currency valuation, accruals, reclassification, "
                    "and balance carryforward.",
        key_transactions=["FAGL_FC_VAL", "FBS1", "F.13", "FAGLGVTR", "AJAB"],
        prerequisites=["BF0", "BF2", "BF4", "BF6"],
        industry_relevance=["all"],
        process_steps=[
            "Open/close posting periods",
            "Foreign currency revaluation (FAGL_FC_VAL)",
            "Accrual/deferral posting",
            "GR/IR clearing (F.13)",
            "Depreciation run (AFAB)",
            "Reclassification (receivables/payables)",
            "Financial statement preparation",
            "Year-end: Balance carryforward (FAGLGVTR)",
        ],
        common_gaps=[
            "Fast close requirements (< 3 business days)",
            "Automated closing cockpit customization",
            "Intercompany elimination in close",
            "Management reporting vs. statutory reporting timelines",
        ],
        test_scenarios=[
            {"name": "Month-End Close", "name_ja": "月次決算処理",
             "steps": [
                 {"t_code": "FAGL_FC_VAL", "action": "Run foreign currency valuation",
                  "input": "Company code, Key date, Exchange rate type",
                  "expected": "Valuation documents posted"},
                 {"t_code": "F.13", "action": "GR/IR clearing",
                  "input": "Company code, Posting date",
                  "expected": "GR/IR items cleared"},
                 {"t_code": "AFAB", "action": "Run depreciation",
                  "input": "Company code, Period",
                  "expected": "Depreciation posted"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="J77",
        name_en="Intercompany Accounting",
        name_ja="会社間会計",
        module="FI",
        category="R2R",
        description="Intercompany transaction processing and reconciliation "
                    "including automatic matching and elimination.",
        key_transactions=["FBU8", "FB01", "FBIC"],
        prerequisites=["BF0"],
        industry_relevance=["all"],
        process_steps=[
            "Intercompany posting (FBU8)",
            "Automatic intercompany document creation",
            "Intercompany reconciliation",
            "Dispute resolution for mismatches",
            "Elimination posting for consolidation",
        ],
        common_gaps=[
            "Complex intercompany netting",
            "Multi-currency intercompany matching",
            "Transfer pricing adjustments in IC accounting",
            "Real-time IC reconciliation across time zones",
        ],
        test_scenarios=[
            {"name": "Intercompany Posting", "name_ja": "会社間転記",
             "steps": [
                 {"t_code": "FBU8", "action": "Post intercompany document",
                  "input": "Sending company, Receiving company, Amount",
                  "expected": "IC documents created in both company codes"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="ERP-R2R-008",
        name_en="Cost Center Accounting",
        name_ja="原価センター会計",
        module="CO",
        category="R2R",
        description="Cost center planning, actual posting, allocation, and "
                    "reporting including activity-based costing.",
        key_transactions=["KS01", "KP06", "KSB1", "KSV5", "KSU5"],
        prerequisites=["BF0"],
        industry_relevance=["all"],
        process_steps=[
            "Cost center master data maintenance",
            "Cost center planning (KP06)",
            "Actual cost posting (automatic from FI)",
            "Cost distribution and assessment",
            "Plan/actual comparison reporting",
        ],
        common_gaps=[
            "Complex multi-dimensional allocation cycles",
            "Activity-based costing with custom cost drivers",
            "Rolling forecast integration",
            "Headcount-based allocation automation",
        ],
        test_scenarios=[
            {"name": "Cost Allocation Cycle", "name_ja": "原価配分サイクル",
             "steps": [
                 {"t_code": "KSV5", "action": "Execute cost distribution",
                  "input": "Cycle, Period, Fiscal year",
                  "expected": "Costs distributed per allocation rules"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="ERP-R2R-009",
        name_en="Profitability Analysis",
        name_ja="収益性分析",
        module="CO",
        category="R2R",
        description="Multi-dimensional profitability analysis (CO-PA) for "
                    "analyzing contribution margins by customer, product, region, etc.",
        key_transactions=["KE21N", "KE24", "KE30"],
        prerequisites=["BF0"],
        industry_relevance=["all"],
        process_steps=[
            "Define profitability segments",
            "Revenue and cost flow to CO-PA",
            "Top-down distribution of overheads",
            "Profitability reporting and drilldown",
        ],
        common_gaps=[
            "Real-time CO-PA with complex derivation rules",
            "Customer/product profitability waterfall analysis",
            "CO-PA planning integration with S&OP",
            "Custom value fields beyond standard",
        ],
        test_scenarios=[
            {"name": "Profitability Report", "name_ja": "収益性分析レポート",
             "steps": [
                 {"t_code": "KE30", "action": "Execute profitability report",
                  "input": "Operating concern, Report form",
                  "expected": "Multi-dimensional profit analysis displayed"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="ERP-R2R-010",
        name_en="Product Costing",
        name_ja="製品原価計算",
        module="CO",
        category="R2R",
        description="Standard cost estimation, actual costing via material ledger, "
                    "and variance analysis.",
        key_transactions=["CK11N", "CK40N", "CKMLCP", "CKM3N"],
        prerequisites=["BF0"],
        industry_relevance=["manufacturing"],
        process_steps=[
            "BOM and routing maintenance",
            "Standard cost estimate creation (CK11N)",
            "Cost estimate marking and release (CK40N)",
            "Actual costing via material ledger (CKMLCP)",
            "Variance analysis (plan vs. actual)",
        ],
        common_gaps=[
            "Multi-level actual costing with complex cost splits",
            "Actual cost component split customization",
            "Joint production / by-product costing",
            "Transfer price calculation in material ledger",
        ],
        test_scenarios=[
            {"name": "Standard Cost Estimate", "name_ja": "標準原価計算",
             "steps": [
                 {"t_code": "CK11N", "action": "Create cost estimate",
                  "input": "Material, Plant, Costing variant",
                  "expected": "Standard cost estimated"},
                 {"t_code": "CK40N", "action": "Mark and release cost estimate",
                  "input": "Costing run parameters",
                  "expected": "Standard price updated in material master"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="ERP-R2R-011",
        name_en="Internal Orders",
        name_ja="内部指図管理",
        module="CO",
        category="R2R",
        description="Overhead cost order management for tracking costs of "
                    "specific activities, projects, or events.",
        key_transactions=["KO01", "KO02", "KOB1", "KO88"],
        prerequisites=["BF0"],
        industry_relevance=["all"],
        process_steps=[
            "Create internal order (KO01)",
            "Budget assignment (optional)",
            "Cost posting to internal order",
            "Order settlement to receivers (KO88)",
            "Order closing",
        ],
        common_gaps=[
            "Complex settlement rules with multiple receivers",
            "Investment order integration with asset under construction",
            "Automated order creation from workflow triggers",
            "Cross-company code internal order reporting",
        ],
        test_scenarios=[
            {"name": "Internal Order Lifecycle", "name_ja": "内部指図ライフサイクル",
             "steps": [
                 {"t_code": "KO01", "action": "Create internal order",
                  "input": "Order type, Description, Cost center",
                  "expected": "Internal order created"},
                 {"t_code": "KO88", "action": "Settle internal order",
                  "input": "Order number, Settlement period",
                  "expected": "Costs settled to receivers"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="ERP-R2R-012",
        name_en="Tax Management",
        name_ja="税務管理",
        module="FI",
        category="R2R",
        description="Tax calculation, tax reporting, and withholding tax management "
                    "including country-specific tax requirements.",
        key_transactions=["FTXP", "S_ALR_87012357", "FB60"],
        prerequisites=["BF0"],
        industry_relevance=["all"],
        process_steps=[
            "Tax code configuration",
            "Automatic tax calculation in documents",
            "Withholding tax processing",
            "Tax reporting (periodic)",
            "Tax audit support",
        ],
        common_gaps=[
            "Country-specific e-invoicing and digital tax reporting",
            "Complex withholding tax scenarios (cascading rates)",
            "Tax determination for complex intercompany transactions",
            "Indirect tax compliance across multiple jurisdictions",
        ],
        test_scenarios=[
            {"name": "Tax Calculation in AP", "name_ja": "買掛金税計算",
             "steps": [
                 {"t_code": "FB60", "action": "Post invoice with tax",
                  "input": "Vendor, Amount, Tax code",
                  "expected": "Tax calculated and posted to tax accounts"},
             ]},
        ],
    ),
]


# ============================================================================
# Plan to Manufacture (P2M) Scope Items
# ============================================================================

P2M_SCOPE_ITEMS: list[ScopeItem] = [
    ScopeItem(
        scope_id="BCF",
        name_en="Make-to-Stock Production",
        name_ja="見込生産",
        module="PP",
        category="P2M",
        description="Standard production process based on planned independent "
                    "requirements. MRP generates planned orders converted to "
                    "production orders.",
        key_transactions=["MD61", "MD01", "CO01", "CO11N", "MIGO"],
        prerequisites=[],
        industry_relevance=["manufacturing"],
        process_steps=[
            "Create planned independent requirements (MD61)",
            "Run MRP (MD01/MD02)",
            "Convert planned orders to production orders (CO40/CO41)",
            "Release production order (CO02)",
            "Material staging / goods issue to production",
            "Production confirmation (CO11N)",
            "Goods receipt of finished product (MIGO)",
            "Production order settlement (KO88/CO88)",
        ],
        common_gaps=[
            "Complex planning strategies (customer-specific MTS)",
            "Demand-driven MRP (DDMRP) requirements",
            "Advanced production scheduling beyond basic SAP",
            "Integration with external MES systems",
        ],
        test_scenarios=[
            {"name": "MTS Production Cycle", "name_ja": "見込生産サイクル",
             "steps": [
                 {"t_code": "MD61", "action": "Create planned independent requirements",
                  "input": "Material, Plant, Period, Quantity",
                  "expected": "PIR created"},
                 {"t_code": "MD01", "action": "Run MRP",
                  "input": "Plant, MRP area",
                  "expected": "Planned orders generated"},
                 {"t_code": "CO01", "action": "Create production order",
                  "input": "Planned order reference",
                  "expected": "Production order created"},
                 {"t_code": "CO11N", "action": "Confirm production",
                  "input": "Order number, Yield quantity",
                  "expected": "Confirmation posted"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="BCI",
        name_en="Make-to-Order Production",
        name_ja="個別受注生産",
        module="PP",
        category="P2M",
        description="Production triggered by individual customer orders. "
                    "Each production order is linked to a specific sales order.",
        key_transactions=["VA01", "MD50", "CO01", "CO11N", "VL01N"],
        prerequisites=["BD1"],
        industry_relevance=["manufacturing"],
        process_steps=[
            "Sales order creation triggers MRP",
            "MRP planning at individual customer order level",
            "Production order linked to sales order",
            "Material procurement for specific order",
            "Production execution and confirmation",
            "Goods receipt to order stock",
            "Delivery from order stock",
        ],
        common_gaps=[
            "Engineer-to-order (ETO) with custom BOM/routing per order",
            "Complex order-specific costing and profitability",
            "Multi-level make-to-order across plants",
            "Order-specific serial number assignment",
        ],
        test_scenarios=[
            {"name": "MTO Production Cycle", "name_ja": "個別受注生産サイクル",
             "steps": [
                 {"t_code": "VA01", "action": "Create MTO sales order",
                  "input": "Customer, Material (MTO strategy), Qty",
                  "expected": "Sales order created, MRP triggered"},
                 {"t_code": "CO01", "action": "Create production order for sales order",
                  "input": "Sales order reference",
                  "expected": "Production order linked to sales order"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="BCK",
        name_en="Repetitive Manufacturing",
        name_ja="繰返製造",
        module="PP",
        category="P2M",
        description="Simplified production execution for high-volume, repetitive "
                    "manufacturing with backflushing. Uses production lines "
                    "instead of discrete production orders.",
        key_transactions=["MF50", "MFBF", "MF42"],
        prerequisites=["BCF"],
        industry_relevance=["manufacturing"],
        process_steps=[
            "Production line/version maintenance",
            "Planning table (MF50)",
            "Backflush posting (MFBF)",
            "Automatic goods issue and goods receipt",
            "Cost collector management",
        ],
        common_gaps=[
            "Mixed-model production line sequencing",
            "Complex backflushing rules (phantom assemblies)",
            "Line balancing and takt time optimization",
            "Integration with production line monitoring systems",
        ],
        test_scenarios=[
            {"name": "Repetitive Manufacturing Cycle", "name_ja": "繰返製造サイクル",
             "steps": [
                 {"t_code": "MF50", "action": "Plan on production line",
                  "input": "Production line, Material, Planned qty",
                  "expected": "Planned quantities assigned to line"},
                 {"t_code": "MFBF", "action": "Backflush confirmation",
                  "input": "Material, Qty, Production line",
                  "expected": "GR posted, components backflushed"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="BCS",
        name_en="Material Requirements Planning (MRP)",
        name_ja="資材所要量計画",
        module="PP",
        category="P2M",
        description="MRP execution for calculating material requirements based on "
                    "demand, stock, and supply. Generates planned orders for "
                    "procurement and production.",
        key_transactions=["MD01", "MD02", "MD04", "MD05", "MD07"],
        prerequisites=[],
        industry_relevance=["manufacturing", "retail"],
        process_steps=[
            "MRP parameters maintenance in material master",
            "MRP run (MD01/MD02)",
            "Planned order review (MD04)",
            "Exception message processing (MD05/MD07)",
            "Planned order conversion to PO or production order",
        ],
        common_gaps=[
            "Demand-driven MRP (DDMRP) with buffer management",
            "Multi-site MRP with complex transportation times",
            "Forecast-based consumption (advanced forecast integration)",
            "MRP with long-term planning simulation",
        ],
        test_scenarios=[
            {"name": "MRP Run and Review", "name_ja": "MRP実行・確認",
             "steps": [
                 {"t_code": "MD01", "action": "Execute MRP run",
                  "input": "Plant, MRP area, Planning scope",
                  "expected": "Planned orders and purchase requisitions generated"},
                 {"t_code": "MD04", "action": "Review stock/requirements list",
                  "input": "Material, Plant",
                  "expected": "Supply/demand situation displayed"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="ERP-P2M-005",
        name_en="BOM and Routing Management",
        name_ja="部品表・作業手順管理",
        module="PP",
        category="P2M",
        description="Bill of materials and routing/recipe master data management "
                    "for production planning and costing.",
        key_transactions=["CS01", "CS02", "CA01", "CA02", "CR01"],
        prerequisites=[],
        industry_relevance=["manufacturing"],
        process_steps=[
            "BOM creation and maintenance (CS01/CS02)",
            "BOM variant management (alternative BOMs)",
            "Routing creation and maintenance (CA01/CA02)",
            "Work center setup (CR01)",
            "Integration with costing and production",
        ],
        common_gaps=[
            "Configurable BOM for variant configuration products",
            "Engineering change management (ECM) with effectivity dates",
            "BOM comparison across revisions",
            "Integration with external PLM systems",
        ],
        test_scenarios=[
            {"name": "BOM and Routing Setup", "name_ja": "BOM・作業手順設定",
             "steps": [
                 {"t_code": "CS01", "action": "Create BOM",
                  "input": "Material, Plant, Components with quantities",
                  "expected": "BOM created with component list"},
                 {"t_code": "CA01", "action": "Create routing",
                  "input": "Material, Plant, Operations with work centers",
                  "expected": "Routing created with operation sequence"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="ERP-P2M-006",
        name_en="Capacity Planning and Scheduling",
        name_ja="能力計画・スケジューリング",
        module="PP",
        category="P2M",
        description="Capacity evaluation, leveling, and detailed production "
                    "scheduling for work centers.",
        key_transactions=["CM01", "CM07", "CM25", "CM21"],
        prerequisites=["BCF"],
        industry_relevance=["manufacturing"],
        process_steps=[
            "Work center capacity definition",
            "Capacity evaluation (CM01/CM07)",
            "Capacity leveling (dispatch)",
            "Detailed scheduling (CM25)",
            "Bottleneck analysis",
        ],
        common_gaps=[
            "Finite capacity scheduling with optimization",
            "Multi-resource scheduling constraints",
            "Integration with external APS (Advanced Planning Systems)",
            "Real-time schedule updates from shop floor",
        ],
        test_scenarios=[
            {"name": "Capacity Evaluation", "name_ja": "能力評価",
             "steps": [
                 {"t_code": "CM07", "action": "Display capacity overview",
                  "input": "Work center, Planning period",
                  "expected": "Capacity load vs. available capacity displayed"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="ERP-P2M-007",
        name_en="Process Manufacturing",
        name_ja="プロセス製造",
        module="PP",
        category="P2M",
        description="Recipe-based process manufacturing for chemical, "
                    "pharmaceutical, and food industries.",
        key_transactions=["C201", "COR1", "COR6N", "MIGO"],
        prerequisites=[],
        industry_relevance=["manufacturing"],
        process_steps=[
            "Master recipe creation (C201)",
            "Process order creation (COR1)",
            "Process order release and execution",
            "Process order confirmation (COR6N)",
            "Co-product and by-product handling",
        ],
        common_gaps=[
            "Batch-specific recipe adjustments",
            "Process parameter recording and deviation management",
            "Potency management for active ingredients",
            "Complex co-product/by-product allocation",
        ],
        test_scenarios=[
            {"name": "Process Manufacturing Cycle", "name_ja": "プロセス製造サイクル",
             "steps": [
                 {"t_code": "COR1", "action": "Create process order",
                  "input": "Material, Plant, Recipe",
                  "expected": "Process order created from recipe"},
                 {"t_code": "COR6N", "action": "Confirm process order",
                  "input": "Order number, Yield qty",
                  "expected": "Confirmation posted"},
             ]},
        ],
    ),
]


# ============================================================================
# Warehouse Management (WM) Scope Items
# ============================================================================

WM_SCOPE_ITEMS: list[ScopeItem] = [
    ScopeItem(
        scope_id="BMG",
        name_en="Inbound Processing",
        name_ja="入荷処理",
        module="WM",
        category="WM",
        description="Warehouse inbound processing including receiving, quality "
                    "inspection, and putaway with strategy determination.",
        key_transactions=["VL31N", "/SCWM/PRDI", "/SCWM/MON"],
        prerequisites=[],
        industry_relevance=["all"],
        process_steps=[
            "Inbound delivery creation",
            "Goods receipt posting",
            "Putaway strategy determination",
            "Warehouse task creation for putaway",
            "Putaway execution and confirmation",
        ],
        common_gaps=[
            "Complex putaway optimization across multiple storage types",
            "ASN (Advance Shipping Notice) integration",
            "Cross-docking rules for fast-moving goods",
            "Quality inspection integration in receiving",
        ],
        test_scenarios=[
            {"name": "Inbound Putaway", "name_ja": "入荷・格納処理",
             "steps": [
                 {"t_code": "/SCWM/PRDI", "action": "Process inbound delivery",
                  "input": "Delivery number",
                  "expected": "Warehouse tasks created for putaway"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="BMI",
        name_en="Outbound Processing",
        name_ja="出荷処理",
        module="WM",
        category="WM",
        description="Warehouse outbound processing including wave management, "
                    "picking, packing, and loading.",
        key_transactions=["VL01N", "/SCWM/WAVE", "/SCWM/PRDO", "/SCWM/MON"],
        prerequisites=[],
        industry_relevance=["all"],
        process_steps=[
            "Outbound delivery creation",
            "Wave assignment and release",
            "Picking task creation",
            "Picking execution (RF/mobile)",
            "Packing and loading",
            "Goods issue confirmation",
        ],
        common_gaps=[
            "Complex wave optimization algorithms",
            "Pick-and-pack vs. pick-then-pack process variants",
            "Voice-directed picking integration",
            "Automated sorting and conveyor integration",
        ],
        test_scenarios=[
            {"name": "Outbound Picking", "name_ja": "出荷・ピッキング処理",
             "steps": [
                 {"t_code": "/SCWM/WAVE", "action": "Create and release wave",
                  "input": "Delivery selection criteria",
                  "expected": "Wave created, picking tasks generated"},
                 {"t_code": "/SCWM/PRDO", "action": "Process outbound delivery",
                  "input": "Delivery number",
                  "expected": "Picking completed, ready for GI"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="BML",
        name_en="Physical Inventory in Warehouse",
        name_ja="倉庫棚卸",
        module="WM",
        category="WM",
        description="Warehouse-level physical inventory including full count, "
                    "cycle counting, and low-stock counting.",
        key_transactions=["/SCWM/PI_MAIN", "/SCWM/PI_CREATE", "MI01", "MI04", "MI07"],
        prerequisites=[],
        industry_relevance=["all"],
        process_steps=[
            "Physical inventory document creation",
            "Count execution (mobile/RF)",
            "Count result entry",
            "Difference analysis",
            "Adjustment posting",
        ],
        common_gaps=[
            "Continuous cycle counting automation",
            "ABC analysis-based counting frequency",
            "Blind count vs. reference count process selection",
            "Count discrepancy investigation workflow",
        ],
        test_scenarios=[
            {"name": "Warehouse Physical Inventory", "name_ja": "倉庫棚卸処理",
             "steps": [
                 {"t_code": "MI01", "action": "Create PI document",
                  "input": "Plant, Storage location, Materials",
                  "expected": "PI document created"},
                 {"t_code": "MI04", "action": "Enter count results",
                  "input": "Counted quantities",
                  "expected": "Counts entered"},
                 {"t_code": "MI07", "action": "Post differences",
                  "input": "Approved differences",
                  "expected": "Inventory adjusted"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="BMN",
        name_en="Internal Warehouse Movements",
        name_ja="倉庫内移動",
        module="WM",
        category="WM",
        description="Bin-to-bin transfers, replenishment, and internal stock "
                    "movements within the warehouse.",
        key_transactions=["/SCWM/ADGI", "/SCWM/REPL", "/SCWM/MON"],
        prerequisites=[],
        industry_relevance=["all"],
        process_steps=[
            "Ad-hoc internal movement request",
            "Replenishment trigger (automatic/manual)",
            "Warehouse task creation",
            "Task execution and confirmation",
        ],
        common_gaps=[
            "Complex replenishment strategies (min/max, demand-based)",
            "Automated storage and retrieval system (AS/RS) integration",
            "Cross-dock area management",
            "Hazardous material zone restrictions",
        ],
        test_scenarios=[
            {"name": "Internal Stock Movement", "name_ja": "倉庫内移動処理",
             "steps": [
                 {"t_code": "/SCWM/ADGI", "action": "Create internal movement",
                  "input": "Source bin, Destination bin, Material, Qty",
                  "expected": "Warehouse task created and completed"},
             ]},
        ],
    ),
]


# ============================================================================
# Quality Management (QM) Scope Items
# ============================================================================

QM_SCOPE_ITEMS: list[ScopeItem] = [
    ScopeItem(
        scope_id="BM8",
        name_en="Quality Inspection in Production",
        name_ja="生産時品質検査",
        module="QM",
        category="QM",
        description="Quality inspection triggered during production including "
                    "in-process inspection and final inspection.",
        key_transactions=["QA01", "QA32", "QA11", "QM01"],
        prerequisites=["BCF"],
        industry_relevance=["manufacturing"],
        process_steps=[
            "Inspection lot creation (automatic from production)",
            "Sample determination",
            "Results recording (QA32)",
            "Usage decision (QA11) - accept/reject",
            "Quality notification for defects (QM01)",
            "Stock posting based on decision",
        ],
        common_gaps=[
            "Real-time SPC (Statistical Process Control) integration",
            "Equipment/instrument calibration integration",
            "Automated test equipment data collection",
            "Complex sampling procedures (skip-lot, AQL)",
        ],
        test_scenarios=[
            {"name": "Production Quality Inspection", "name_ja": "生産品質検査",
             "steps": [
                 {"t_code": "QA32", "action": "Record inspection results",
                  "input": "Inspection lot, Characteristic values",
                  "expected": "Results recorded"},
                 {"t_code": "QA11", "action": "Make usage decision",
                  "input": "Inspection lot, Decision code (accept/reject)",
                  "expected": "Stock posted per decision"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="BMA",
        name_en="Quality Inspection in Procurement",
        name_ja="購買時品質検査",
        module="QM",
        category="QM",
        description="Incoming inspection for purchased materials triggered by "
                    "goods receipt. Includes vendor quality scoring.",
        key_transactions=["QA01", "QA32", "QA11", "QM01"],
        prerequisites=["BMD"],
        industry_relevance=["manufacturing", "retail"],
        process_steps=[
            "Inspection lot auto-created at goods receipt",
            "Material moved to inspection stock",
            "Sample drawing and inspection",
            "Results recording",
            "Usage decision (accept/reject/return to vendor)",
            "Vendor quality score update",
        ],
        common_gaps=[
            "Skip-lot inspection for trusted vendors",
            "Certificate of Analysis (CoA) management",
            "Supplier corrective action request (SCAR) workflow",
            "Shelf-life and expiry date verification at receipt",
        ],
        test_scenarios=[
            {"name": "Incoming Inspection", "name_ja": "受入検査",
             "steps": [
                 {"t_code": "MIGO", "action": "Post GR triggering inspection",
                  "input": "PO reference, Material with inspection active",
                  "expected": "GR posted, inspection lot created"},
                 {"t_code": "QA32", "action": "Record inspection results",
                  "input": "Inspection lot, Measured values",
                  "expected": "Results recorded for all characteristics"},
                 {"t_code": "QA11", "action": "Usage decision",
                  "input": "Accept/Reject, Follow-up action",
                  "expected": "Stock moved to unrestricted (accept) or blocked (reject)"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="ERP-QM-003",
        name_en="Quality Notification and CAPA",
        name_ja="品質通知・是正予防措置",
        module="QM",
        category="QM",
        description="Quality notification processing for defect tracking, "
                    "complaint management, and corrective/preventive actions.",
        key_transactions=["QM01", "QM02", "QM03"],
        prerequisites=[],
        industry_relevance=["all"],
        process_steps=[
            "Create quality notification (QM01)",
            "Defect recording with catalog codes",
            "Root cause analysis",
            "Corrective action assignment",
            "Preventive action planning",
            "Notification completion and follow-up",
        ],
        common_gaps=[
            "Complex CAPA workflow with escalation rules",
            "Integration with document management for evidence",
            "Automated notification creation from IoT/sensor data",
            "8D report generation",
        ],
        test_scenarios=[
            {"name": "CAPA Process", "name_ja": "是正予防措置プロセス",
             "steps": [
                 {"t_code": "QM01", "action": "Create quality notification",
                  "input": "Notification type, Material, Defect code",
                  "expected": "Notification created with tasks"},
                 {"t_code": "QM02", "action": "Process corrective actions",
                  "input": "Task completion, Root cause",
                  "expected": "Actions completed, notification closed"},
             ]},
        ],
    ),
]


# ============================================================================
# Asset Management (AM) / Plant Maintenance Scope Items
# ============================================================================

AM_SCOPE_ITEMS: list[ScopeItem] = [
    ScopeItem(
        scope_id="ERP-AM-001",
        name_en="Preventive Maintenance",
        name_ja="予防保全",
        module="PM",
        category="AM",
        description="Time-based and performance-based preventive maintenance "
                    "planning and execution.",
        key_transactions=["IP01", "IP02", "IP10", "IP30", "IW31"],
        prerequisites=[],
        industry_relevance=["manufacturing", "service"],
        process_steps=[
            "Maintenance plan creation (IP01)",
            "Scheduling parameters definition",
            "Plan scheduling (IP10)",
            "Maintenance call generation (IP30)",
            "Maintenance order creation",
            "Order execution and confirmation",
        ],
        common_gaps=[
            "Condition-based maintenance with IoT sensor integration",
            "Predictive maintenance using machine learning",
            "Complex scheduling across multiple maintenance plans",
            "Maintenance window optimization",
        ],
        test_scenarios=[
            {"name": "Preventive Maintenance Cycle", "name_ja": "予防保全サイクル",
             "steps": [
                 {"t_code": "IP10", "action": "Schedule maintenance plan",
                  "input": "Maintenance plan, Scheduling period",
                  "expected": "Maintenance calls generated"},
                 {"t_code": "IW31", "action": "Create maintenance order",
                  "input": "Notification/plan reference",
                  "expected": "Maintenance order created"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="ERP-AM-002",
        name_en="Corrective Maintenance",
        name_ja="事後保全",
        module="PM",
        category="AM",
        description="Reactive maintenance for unplanned equipment failures "
                    "including notification, order, and repair execution.",
        key_transactions=["IW21", "IW31", "IW32", "IW41"],
        prerequisites=[],
        industry_relevance=["manufacturing", "service"],
        process_steps=[
            "Malfunction notification creation (IW21)",
            "Maintenance order creation (IW31)",
            "Spare parts reservation and procurement",
            "Order release and execution",
            "Work confirmation (IW41)",
            "Technical completion and cost settlement",
        ],
        common_gaps=[
            "Emergency maintenance prioritization rules",
            "Technician dispatching and skill-based assignment",
            "Mobile maintenance execution",
            "Spare part availability check integration",
        ],
        test_scenarios=[
            {"name": "Breakdown Repair", "name_ja": "故障修理プロセス",
             "steps": [
                 {"t_code": "IW21", "action": "Create malfunction notification",
                  "input": "Equipment, Damage code, Priority",
                  "expected": "Notification created"},
                 {"t_code": "IW31", "action": "Create maintenance order",
                  "input": "Notification reference, Operations",
                  "expected": "Order created with planned operations"},
                 {"t_code": "IW41", "action": "Confirm maintenance work",
                  "input": "Order, Actual work time, Materials used",
                  "expected": "Work confirmed, costs posted"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="ERP-AM-003",
        name_en="Equipment and Functional Location Management",
        name_ja="設備・機能場所管理",
        module="PM",
        category="AM",
        description="Technical object management including equipment master data, "
                    "functional location hierarchy, and asset structure.",
        key_transactions=["IE01", "IE02", "IL01", "IL02"],
        prerequisites=[],
        industry_relevance=["manufacturing", "service"],
        process_steps=[
            "Functional location hierarchy definition",
            "Equipment master creation",
            "Equipment installation at functional locations",
            "Classification and characteristics assignment",
            "Measurement point management",
        ],
        common_gaps=[
            "Integration with GIS systems for location management",
            "Digital twin integration",
            "Complex linear asset management (pipelines, railways)",
            "Asset hierarchy import from legacy systems",
        ],
        test_scenarios=[
            {"name": "Equipment Setup", "name_ja": "設備マスタ設定",
             "steps": [
                 {"t_code": "IL01", "action": "Create functional location",
                  "input": "Location label, Description, Category",
                  "expected": "Functional location created"},
                 {"t_code": "IE01", "action": "Create equipment",
                  "input": "Description, Equipment category, Location",
                  "expected": "Equipment created and installed"},
             ]},
        ],
    ),
]


# ============================================================================
# Human Capital Management (HCM) Scope Items
# ============================================================================

HCM_SCOPE_ITEMS: list[ScopeItem] = [
    ScopeItem(
        scope_id="BHR",
        name_en="Employee Master Data Management",
        name_ja="従業員マスタデータ管理",
        module="HR",
        category="HCM",
        description="Employee master data management including personal data, "
                    "organizational assignment, and personnel actions.",
        key_transactions=["PA20", "PA30", "PA40", "PPOME"],
        prerequisites=[],
        industry_relevance=["all"],
        process_steps=[
            "Organizational structure maintenance (PPOME)",
            "Employee hiring action (PA40)",
            "Personnel data maintenance (PA30)",
            "Personnel actions (promotion, transfer, termination)",
            "Reporting and analytics",
        ],
        common_gaps=[
            "Complex organizational structure with matrix organizations",
            "Global HR data model across countries",
            "Integration with external recruitment systems",
            "Employee self-service for data maintenance",
        ],
        test_scenarios=[
            {"name": "Employee Hiring", "name_ja": "採用処理",
             "steps": [
                 {"t_code": "PA40", "action": "Execute hiring action",
                  "input": "Personnel number, Start date, Org unit, Position",
                  "expected": "Employee hired with all infotypes created"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="BHS",
        name_en="Payroll Processing",
        name_ja="給与計算処理",
        module="HR",
        category="HCM",
        description="Gross-to-net payroll processing including statutory "
                    "deductions, benefits, and payment.",
        key_transactions=["PC00_M99_RUN", "PC_PAYRESULT", "PC00_M99_CEDT"],
        prerequisites=["BHR"],
        industry_relevance=["all"],
        process_steps=[
            "Payroll area and period definition",
            "Master data verification",
            "Payroll simulation",
            "Payroll run execution",
            "Payroll results review",
            "Bank transfer creation",
            "Payslip generation",
            "Posting to FI/CO",
        ],
        common_gaps=[
            "Country-specific payroll regulations",
            "Complex union/collective agreement rules",
            "Retroactive payroll across multiple periods",
            "Integration with external payroll providers",
        ],
        test_scenarios=[
            {"name": "Monthly Payroll", "name_ja": "月次給与計算",
             "steps": [
                 {"t_code": "PC00_M99_RUN", "action": "Execute payroll run",
                  "input": "Payroll area, Period, Simulation mode",
                  "expected": "Payroll calculated for all employees"},
                 {"t_code": "PC_PAYRESULT", "action": "Review payroll results",
                  "input": "Personnel number",
                  "expected": "Gross-to-net calculation verified"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="BHU",
        name_en="Time Management",
        name_ja="勤怠管理",
        module="HR",
        category="HCM",
        description="Work schedule management, time recording, absence management, "
                    "and time evaluation for payroll integration.",
        key_transactions=["PA61", "PA62", "PT01", "PT60"],
        prerequisites=["BHR"],
        industry_relevance=["all"],
        process_steps=[
            "Work schedule definition",
            "Time recording (positive/negative)",
            "Absence recording (leave, sick)",
            "Overtime approval",
            "Time evaluation execution (PT60)",
            "Transfer to payroll",
        ],
        common_gaps=[
            "Complex shift patterns and rotation schedules",
            "Flexible working time accounts",
            "Integration with physical time clock systems",
            "Country-specific leave regulations",
        ],
        test_scenarios=[
            {"name": "Time Recording and Evaluation", "name_ja": "勤怠記録・評価",
             "steps": [
                 {"t_code": "PA61", "action": "Record attendance",
                  "input": "Personnel number, Date, Times",
                  "expected": "Attendance recorded"},
                 {"t_code": "PT60", "action": "Run time evaluation",
                  "input": "Personnel number, Period",
                  "expected": "Time balances calculated, overtime determined"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="ERP-HCM-004",
        name_en="Leave Management",
        name_ja="休暇管理",
        module="HR",
        category="HCM",
        description="Leave entitlement calculation, leave request processing, "
                    "and leave balance tracking.",
        key_transactions=["PA61", "PT50", "PT_QUOMO"],
        prerequisites=["BHR", "BHU"],
        industry_relevance=["all"],
        process_steps=[
            "Leave entitlement generation",
            "Leave request creation",
            "Approval workflow",
            "Leave balance tracking",
            "Leave accrual and carryover",
        ],
        common_gaps=[
            "Complex leave policies (accrual rules, carryover limits)",
            "Integration with project planning for resource availability",
            "Leave request via mobile/self-service",
            "Country-specific mandatory leave rules",
        ],
        test_scenarios=[
            {"name": "Leave Request Process", "name_ja": "休暇申請プロセス",
             "steps": [
                 {"t_code": "PA61", "action": "Enter leave request",
                  "input": "Personnel number, Absence type, Date range",
                  "expected": "Leave recorded, balance reduced"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="ERP-HCM-005",
        name_en="Organizational Management",
        name_ja="組織管理",
        module="HR",
        category="HCM",
        description="Organizational structure management including positions, "
                    "jobs, and reporting relationships.",
        key_transactions=["PPOME", "PO10", "PO13", "PPOSE"],
        prerequisites=[],
        industry_relevance=["all"],
        process_steps=[
            "Organizational unit creation and hierarchy",
            "Position definition and staffing",
            "Job catalog maintenance",
            "Reporting structure definition",
            "Organization visualization",
        ],
        common_gaps=[
            "Matrix organization modeling",
            "Dynamic org chart generation for external systems",
            "Position budgeting and headcount control",
            "Integration with talent management and succession planning",
        ],
        test_scenarios=[
            {"name": "Org Structure Setup", "name_ja": "組織構造設定",
             "steps": [
                 {"t_code": "PPOME", "action": "Maintain org structure",
                  "input": "Org units, Positions, Reporting lines",
                  "expected": "Org structure created with positions"},
             ]},
        ],
    ),
]


# ============================================================================
# Cross-process / Additional Scope Items
# ============================================================================

CROSS_PROCESS_SCOPE_ITEMS: list[ScopeItem] = [
    ScopeItem(
        scope_id="ERP-XP-001",
        name_en="Output Management",
        name_ja="帳票管理",
        module="SD",
        category="O2C",
        description="Output management for business documents including "
                    "order confirmations, delivery notes, invoices, and "
                    "purchase orders across all modules.",
        key_transactions=["NACE", "VV31", "SP01", "SPAD"],
        prerequisites=[],
        industry_relevance=["all"],
        process_steps=[
            "Output type definition",
            "Output determination (condition technique)",
            "Output processing (print, email, EDI, IDoc)",
            "Output monitoring and reprocessing",
        ],
        common_gaps=[
            "Custom form development beyond standard Adobe/SAPscript",
            "E-invoicing format requirements (country-specific)",
            "Dynamic output routing based on customer preferences",
            "Archive integration for output documents",
        ],
        test_scenarios=[
            {"name": "Invoice Output", "name_ja": "請求書帳票出力",
             "steps": [
                 {"t_code": "VF02", "action": "Display invoice and trigger output",
                  "input": "Billing document number",
                  "expected": "Invoice PDF generated and sent"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="ERP-XP-002",
        name_en="Batch Management",
        name_ja="ロット管理",
        module="MM",
        category="P2P",
        description="Cross-module batch management for traceability including "
                    "batch creation, classification, determination, and "
                    "where-used analysis.",
        key_transactions=["MSC1N", "MSC2N", "MSC3N", "MB56"],
        prerequisites=[],
        industry_relevance=["manufacturing", "retail"],
        process_steps=[
            "Batch master creation",
            "Batch classification with characteristics",
            "Batch determination in sales/production",
            "Batch where-used (forward/backward traceability)",
            "Shelf life and expiry management",
        ],
        common_gaps=[
            "Complex batch splitting and merging rules",
            "Batch genealogy across multiple production levels",
            "Customer-specific batch requirements",
            "Batch recall process automation",
        ],
        test_scenarios=[
            {"name": "Batch Traceability", "name_ja": "ロット追跡",
             "steps": [
                 {"t_code": "MB56", "action": "Batch where-used analysis",
                  "input": "Batch number, Material",
                  "expected": "Forward and backward traceability displayed"},
             ]},
        ],
    ),
    ScopeItem(
        scope_id="ERP-XP-003",
        name_en="Profit Center Accounting",
        name_ja="利益センター会計",
        module="CO",
        category="R2R",
        description="Profit center management for internal profitability "
                    "analysis by business segment, product line, or region.",
        key_transactions=["KE51", "KE5Z", "1KE5", "8KE5"],
        prerequisites=["BF0"],
        industry_relevance=["all"],
        process_steps=[
            "Profit center hierarchy definition",
            "Profit center assignment rules",
            "Revenue and cost flow to profit centers",
            "Transfer pricing between profit centers",
            "Profit center P&L reporting",
        ],
        common_gaps=[
            "Complex profit center derivation rules",
            "Multi-dimensional profit center hierarchies",
            "Transfer pricing for intercompany and inter-profit-center",
            "Profit center budgeting integration",
        ],
        test_scenarios=[
            {"name": "Profit Center Report", "name_ja": "利益センターレポート",
             "steps": [
                 {"t_code": "KE5Z", "action": "Display profit center P&L",
                  "input": "Profit center, Fiscal year, Period range",
                  "expected": "Revenue and cost displayed by profit center"},
             ]},
        ],
    ),
]


# ============================================================================
# Registry and Lookup Functions
# ============================================================================

# All scope items in a flat list
ALL_SCOPE_ITEMS: list[ScopeItem] = (
    O2C_SCOPE_ITEMS
    + P2P_SCOPE_ITEMS
    + R2R_SCOPE_ITEMS
    + P2M_SCOPE_ITEMS
    + WM_SCOPE_ITEMS
    + QM_SCOPE_ITEMS
    + AM_SCOPE_ITEMS
    + HCM_SCOPE_ITEMS
    + CROSS_PROCESS_SCOPE_ITEMS
)

# Index by scope_id for fast lookup
_SCOPE_INDEX: dict[str, ScopeItem] = {item.scope_id: item for item in ALL_SCOPE_ITEMS}

# Index by module
_MODULE_INDEX: dict[str, list[ScopeItem]] = {}
for _item in ALL_SCOPE_ITEMS:
    _MODULE_INDEX.setdefault(_item.module, []).append(_item)

# Index by category
_CATEGORY_INDEX: dict[str, list[ScopeItem]] = {}
for _item in ALL_SCOPE_ITEMS:
    _CATEGORY_INDEX.setdefault(_item.category, []).append(_item)


def get_scope_item(scope_id: str) -> ScopeItem | None:
    """Get a scope item by its ID."""
    return _SCOPE_INDEX.get(scope_id)


def get_scope_items_by_module(module: str) -> list[ScopeItem]:
    """Get all scope items for a given SAP module (e.g., 'SD', 'MM')."""
    return _MODULE_INDEX.get(module.upper(), [])


def get_scope_items_by_category(category: str) -> list[ScopeItem]:
    """Get all scope items for a given business process category (e.g., 'O2C', 'P2P')."""
    return _CATEGORY_INDEX.get(category.upper(), [])


def get_all_scope_items() -> list[ScopeItem]:
    """Get all scope items."""
    return ALL_SCOPE_ITEMS


def get_all_categories() -> dict[str, dict[str, str]]:
    """Get all process categories with descriptions."""
    return PROCESS_CATEGORIES


def search_scope_items(keyword: str) -> list[ScopeItem]:
    """Search scope items by keyword across name, description, and transactions."""
    keyword_lower = keyword.lower()
    results: list[ScopeItem] = []
    for item in ALL_SCOPE_ITEMS:
        if (
            keyword_lower in item.name_en.lower()
            or keyword_lower in item.name_ja
            or keyword_lower in item.description.lower()
            or keyword_lower in item.scope_id.lower()
            or any(keyword_lower in t.lower() for t in item.key_transactions)
        ):
            results.append(item)
    return results


def get_scope_item_summary() -> list[dict[str, str]]:
    """Get a summary list of all scope items."""
    return [
        {
            "scope_id": item.scope_id,
            "name_en": item.name_en,
            "name_ja": item.name_ja,
            "module": item.module,
            "category": item.category,
        }
        for item in ALL_SCOPE_ITEMS
    ]


def get_common_gaps_for_module(module: str) -> list[dict[str, Any]]:
    """Get common gap patterns for all scope items in a module."""
    results: list[dict[str, Any]] = []
    for item in get_scope_items_by_module(module):
        if item.common_gaps:
            results.append({
                "scope_id": item.scope_id,
                "name_en": item.name_en,
                "name_ja": item.name_ja,
                "common_gaps": item.common_gaps,
            })
    return results


def get_test_scenarios_for_scope_item(scope_id: str) -> list[dict[str, Any]]:
    """Get test scenarios for a specific scope item."""
    item = get_scope_item(scope_id)
    if item is None:
        return []
    return item.test_scenarios
