package mesosphere.marathon
package api

import java.util.concurrent.atomic.AtomicInteger
import javax.inject.Provider

import akka.event.EventStream
import com.codahale.metrics.MetricRegistry
import mesosphere.AkkaTest
import mesosphere.marathon.core.group.GroupManagerModule
import mesosphere.marathon.core.leadership.AlwaysElectedLeadershipModule
import mesosphere.marathon.io.storage.StorageProvider
import mesosphere.marathon.metrics.Metrics
import mesosphere.marathon.storage.repository.{ AppRepository, GroupRepository, PodRepository }
import mesosphere.marathon.test.Mockito

class TestGroupManagerFixture extends Mockito with AkkaTest {
  val service = mock[MarathonSchedulerService]
  val groupRepository = mock[GroupRepository]
  val podRepository = mock[PodRepository]
  val appRepository = mock[AppRepository]
  val eventBus = mock[EventStream]
  val provider = mock[StorageProvider]

  val config = AllConf.withTestConfig("--zk_timeout", "1000")

  val metricRegistry = new MetricRegistry()
  val metrics = new Metrics(metricRegistry)

  val actorId = new AtomicInteger(0)

  val schedulerProvider = new Provider[DeploymentService] {
    override def get() = service
  }

  private[this] val groupManagerModule = GroupManagerModule(config)(
    AlwaysElectedLeadershipModule.forActorSystem(system),
    scheduler = schedulerProvider,
    groupRepo = groupRepository,
    appRepo = appRepository,
    podRepo = podRepository,
    storage = provider,
    eventBus = eventBus,
    mat = mat,
    metrics = metrics)

  val groupManager = groupManagerModule.groupManager
}
