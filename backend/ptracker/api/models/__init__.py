from .candidate import Candidate, CandidateBase, CandidateCreate, CandidatePublic, CandidatesPublic, CandidateUpdate
from .promise import Promise, PromiseBase, PromiseCreate
from .source import Source, SourceBase, SourceCreate


# Resolve a few tricky types for Pydantic directly.
CandidateCreate.model_rebuild()
PromiseCreate.model_rebuild()
