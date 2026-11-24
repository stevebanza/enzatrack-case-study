# Excerpt from EnzaTrack (full source is private). Shown to illustrate the design;
# it depends on the application's models and is not runnable on its own.
# © Steve KUBENGA BANZA. All rights reserved.

from django.db import models
from django.db.models import Q, Subquery

from core.models.org_partners import OrgPartner

class LessonLearnedQuerySet(models.QuerySet):
    def visible_to(self, user):
        Model = self.model
        base = self.filter(status=Model.Status.APPROVED)
   
        # Anonymous → PUBLIC only
        if not user or not getattr(user, "is_authenticated", False):
            return base.filter(visibility=Model.Visibility.PUBLIC)

        profile = getattr(user, "userprofile", None)
        org_id  = getattr(profile, "organization_id", None)
        is_partner_user = getattr(profile, "is_partner_user", False)
        partner_of_org  = getattr(profile, "partner_of_org_id", None)

        public_q = Q(visibility=Model.Visibility.PUBLIC)

        # (Optional) Superusers can see all approved
        if getattr(user, "is_superuser", False):
            return base

        if org_id:
            # Internal user: see all three visibilities within same org + PUBLIC anywhere
            same_org_q = Q(organization_id=org_id) & Q(
                visibility__in=[Model.Visibility.PRIVATE, Model.Visibility.PARTNER, Model.Visibility.PUBLIC]
            )
            # PARTNER from hosts that share with my org
            # Use a Subquery (no Python list materialization)
            partner_host_ids = Subquery(
                OrgPartner.objects.filter(partner_org_id=org_id, can_view_lessons=True)
                                  .values("host_org_id")
            )
            partner_from_hosts_q = Q(visibility=Model.Visibility.PARTNER,
                                     organization_id__in=partner_host_ids)
            return base.filter(public_q | same_org_q | partner_from_hosts_q)

        if is_partner_user and partner_of_org:
            partner_host_ids = Subquery(
                OrgPartner.objects.filter(partner_org_id=partner_of_org, can_view_lessons=True)
                                  .values("host_org_id")
            )
            partner_from_hosts_q = Q(visibility=Model.Visibility.PARTNER,
                                     organization_id__in=partner_host_ids)
            return base.filter(public_q | partner_from_hosts_q)

        # Authenticated but no org info → PUBLIC only
        return base.filter(public_q)
