# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import plomino.directupload


class PlominoDirectuploadLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=plomino.directupload)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plomino.directupload:default')


PLOMINO_DIRECTUPLOAD_FIXTURE = PlominoDirectuploadLayer()


PLOMINO_DIRECTUPLOAD_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLOMINO_DIRECTUPLOAD_FIXTURE,),
    name='PlominoDirectuploadLayer:IntegrationTesting'
)


PLOMINO_DIRECTUPLOAD_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLOMINO_DIRECTUPLOAD_FIXTURE,),
    name='PlominoDirectuploadLayer:FunctionalTesting'
)


PLOMINO_DIRECTUPLOAD_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        PLOMINO_DIRECTUPLOAD_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='PlominoDirectuploadLayer:AcceptanceTesting'
)
