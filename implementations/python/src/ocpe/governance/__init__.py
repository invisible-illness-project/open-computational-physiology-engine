"""
OCPE governance extension (OPTIONAL).

Evidence-layered review tracking per ADR 0001 (review manifest v2.0.0), split
into three independent layers:

* :mod:`ocpe.governance.manifest`      - review records (sidecar data model + I/O)
* :mod:`ocpe.governance.aggregation`   - derived summary of review activity
* :mod:`ocpe.governance.authorization` - organisation-specific downstream-use policy

None of these are needed to load, validate or resolve OCPE packages; the core
engine (:mod:`ocpe.loader`, :mod:`ocpe.validator`, :mod:`ocpe.resolver`) never
imports this package.
"""

from .manifest import (  # noqa: F401
    AUTHORIZATION_STATUSES,
    AUTHORIZATION_USES,
    CHALLENGE_STATUSES,
    HUMAN_REVIEW_STATUSES,
    MANIFEST_VERSION,
    VALID_REVIEWER_KINDS,
    VALID_VERDICTS,
    VALIDATION_STATES,
    Adjudication,
    AuthorizationPolicyStatus,
    Challenge,
    Claim,
    ClaimEvidence,
    DerivedValidationSummary,
    Finding,
    HumanReviewBlock,
    HumanReviewEntry,
    ReviewEvent,
    Reviewer,
    ReviewerIdentity,
    SidecarManifest,
    TargetFile,
    compute_sha256,
    get_sidecar_path,
    load_sidecar,
    migrate_v1_dict_to_v2,
    save_sidecar,
)
from .aggregation import aggregate_validation  # noqa: F401
from .authorization import check_authorization  # noqa: F401
