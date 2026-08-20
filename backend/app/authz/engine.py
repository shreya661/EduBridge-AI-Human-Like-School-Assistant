# backend/app/authz/engine.py
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from .models import AuthorizationResult, AuthorizationDecision, ResourceTarget
from ..session.models import Identity, Role
from .rbac_table import has_permission
from .ownership import validate_ownership
import logging


class AuthorizationEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def authorize_request(
        self,
        identity: Identity,
        intent: str,
        target_data: Optional[Dict[str, Any]] = None
    ) -> AuthorizationResult:
        """
        Main authorization entry point
        Returns deterministic authorization result
        """
        # Map intent to operation and resource
        operation, resource_target = self._map_intent_to_operation(intent, target_data)
        
        if not operation:
            return AuthorizationResult(
                decision=AuthorizationDecision.DENIED,
                allowed=False,
                reason="UNKNOWN_INTENT",
                user_id=identity.user_id,
                role=identity.role.value,
                operation=intent,
                resource_type=resource_target.resource_type if resource_target else None,
                resource_id=resource_target.resource_id if resource_target else None,
                timestamp=datetime.utcnow().isoformat()
            )
        
        # Check RBAC permission
        if not has_permission(identity.role, operation):
            return AuthorizationResult(
                decision=AuthorizationDecision.DENIED,
                allowed=False,
                reason="PERMISSION_DENIED",
                user_id=identity.user_id,
                role=identity.role.value,
                operation=operation,
                resource_type=resource_target.resource_type if resource_target else None,
                resource_id=resource_target.resource_id if resource_target else None,
                timestamp=datetime.utcnow().isoformat()
            )
        
        # Check resource ownership/scoping if applicable
        if resource_target and self._requires_ownership_check(operation):
            is_authorized = self._check_resource_ownership(identity, resource_target)
            if not is_authorized:
                return AuthorizationResult(
                    decision=AuthorizationDecision.DENIED,
                    allowed=False,
                    reason="RESOURCE_NOT_ALLOWED",
                    user_id=identity.user_id,
                    role=identity.role.value,
                    operation=operation,
                    resource_type=resource_target.resource_type,
                    resource_id=resource_target.resource_id,
                    timestamp=datetime.utcnow().isoformat()
                )
        
        # Log successful authorization
        self.logger.info(f"Authorization granted: {identity.user_id} ({identity.role}) -> {operation} on {resource_target}")
        
        return AuthorizationResult(
            decision=AuthorizationDecision.ALLOWED,
            allowed=True,
            reason="AUTHORIZED",
            user_id=identity.user_id,
            role=identity.role.value,
            operation=operation,
            resource_type=resource_target.resource_type if resource_target else None,
            resource_id=resource_target.resource_id if resource_target else None,
            timestamp=datetime.utcnow().isoformat()
        )
    
    def _map_intent_to_operation(self, intent: str, target_data: Optional[Dict[str, Any]]) -> Tuple[Optional[str], Optional[ResourceTarget]]:
        """
        Map natural language intent to concrete operation and resource
        This is deterministic, not based on LLM interpretation
        """
        intent_mapping = {
            # Student operations
            "view_own_profile": ("view_own_profile", None),
            "view_own_grades": ("view_own_grades", None),
            "view_own_attendance": ("view_own_attendance", None),
            "submit_assignment": ("submit_assignment", None),
            
            # Parent operations
            "view_child_profile": ("view_child_profile", self._extract_student_target(target_data)),
            "view_child_grades": ("view_child_grades", self._extract_student_target(target_data)),
            "view_child_attendance": ("view_child_attendance", self._extract_student_target(target_data)),
            "communicate_with_teachers": ("communicate_with_teachers", self._extract_student_target(target_data)),
            
            # Teacher operations
            "view_class_roster": ("view_class_roster", self._extract_class_target(target_data)),
            "view_student_profiles": ("view_student_profiles", self._extract_student_target(target_data)),
            "view_student_grades": ("view_student_grades", self._extract_student_target(target_data)),
            "view_student_attendance": ("view_student_attendance", self._extract_student_target(target_data)),
            "manage_assignments": ("manage_assignments", self._extract_class_target(target_data)),
            "grade_submissions": ("grade_submissions", self._extract_student_target(target_data)),
            "mark_attendance": ("mark_attendance", self._extract_student_target(target_data)),
            
            # Principal operations
            "view_all_students": ("view_all_students", None),
            "view_all_teachers": ("view_all_teachers", None),
            "view_all_classes": ("view_all_classes", None),
            "manage_school_settings": ("manage_school_settings", None),
            "generate_reports": ("generate_reports", None),
            "view_all_attendance": ("view_all_attendance", None),
            "manage_users": ("manage_users", None),

            # Escalation operations
            "escalate_to_teacher": ("escalate_to_teacher", None),
            "escalate_to_management": ("escalate_to_management", None),

            # Analytics & School-wide operations
            "view_school_attendance": ("view_school_attendance", None),
            "view_school_analytics": ("view_school_analytics", None),
            "general_school_query": ("general_school_query", None),
        }
        
        return intent_mapping.get(intent, (None, None))
    
    def _extract_student_target(self, target_data: Optional[Dict[str, Any]]) -> Optional[ResourceTarget]:
        if not target_data:
            return None
        
        student_id = target_data.get("target_student_id") or target_data.get("student_id")
        if student_id:
            return ResourceTarget(resource_type="STUDENT", resource_id=student_id)
        return None
    
    def _extract_class_target(self, target_data: Optional[Dict[str, Any]]) -> Optional[ResourceTarget]:
        if not target_data:
            return None
        
        class_id = target_data.get("target_class_id") or target_data.get("class_id")
        if class_id:
            return ResourceTarget(resource_type="CLASS", resource_id=class_id)
        return None
    
    def _requires_ownership_check(self, operation: str) -> bool:
        """
        Determine if an operation requires ownership/scoping validation
        """
        # Operations that require ownership validation
        ownership_required_operations = {
            "view_child_profile",
            "view_child_grades", 
            "view_child_attendance",
            "communicate_with_teachers",
            "view_class_roster",
            "view_student_profiles",
            "view_student_grades",
            "view_student_attendance",
            "manage_assignments",
            "grade_submissions",
            "mark_attendance",
        }
        
        return operation in ownership_required_operations
    
    def _check_resource_ownership(self, identity: Identity, resource_target: ResourceTarget) -> bool:
        """
        Check if identity has ownership/scope access to resource
        """
        if resource_target.resource_type == "STUDENT":
            return bool(validate_ownership(identity, resource_target.resource_id))
        elif resource_target.resource_type == "CLASS":
            # For class resources, check if teacher is assigned to that class
            if identity.role == Role.TEACHER:
                from ..domain import school_domain_service
                assigned_classes = school_domain_service.get_classes_for_teacher(identity.user_id)
                return resource_target.resource_id in [c.class_id for c in assigned_classes]
            elif identity.role == Role.PRINCIPAL:
                # Principal can access any class
                return True
            else:
                # Other roles don't typically access class resources directly
                return False
        
        return False
