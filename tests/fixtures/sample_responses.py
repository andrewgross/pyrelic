METRIC_DATA_SAMPLE = """
<?xml version="1.0" encoding="UTF-8"?>
<metrics type="array">
  <metric app="My Application" agent_id="123456" begin="2011-04-20T15:47:00Z" end="2011-04-20T15:48:00Z" name="ActiveRecord/all">
    <field type="integer" name="average_response_time">0</field>
  </metric>
  <metric app="My Application" agent_id="123456" begin="2011-04-20T15:48:00Z" end="2011-04-20T15:49:00Z" name="ActiveRecord/all">
    <field type="integer" name="average_response_time">0</field>
  </metric>
  <metric app="My Application" agent_id="123456" begin="2011-04-20T15:49:00Z" end="2011-04-20T15:50:00Z" name="ActiveRecord/all">
    <field type="integer" name="average_response_time">0</field>
  </metric>
  <metric app="My Application" agent_id="123456" begin="2011-04-20T15:50:00Z" end="2011-04-20T15:51:00Z" name="ActiveRecord/all">
    <field type="integer" name="average_response_time">0</field>
  </metric>
  <metric app="My Application" agent_id="123456" begin="2011-04-20T15:51:00Z" end="2011-04-20T15:52:00Z" name="ActiveRecord/all">
    <field type="integer" name="average_response_time">0</field>
  </metric>
</metrics>
"""

METRIC_NAMES_SAMPLE = """
<?xml version="1.0" encoding="UTF-8"?>
<metrics type="array">
  <metric name="WebTransaction">
    <fields type="array">
      <field name="average_call_time"/>
      <field name="average_response_time"/>
      <field name="call_count"/>
      <field name="max_call_time"/>
      <field name="min_call_time"/>
      <field name="requests_per_minute"/>
      <field name="throughput"/>
      <field name="total_call_time"/>
    </fields>
  </metric>
  <metric name="WebTransaction/RPMCollector/AgentListener/connect">
    <fields type="array">
      <field name="average_call_time"/>
      <field name="average_response_time"/>
      <field name="call_count"/>
      <field name="max_call_time"/>
      <field name="min_call_time"/>
      <field name="requests_per_minute"/>
      <field name="throughput"/>
      <field name="total_call_time"/>
    </fields>
  </metric>
</metrics>
"""

VIEW_APPLICATIONS_SAMPLE = """
<?xml version="1.0" encoding="UTF-8"?>
<applications type="array">
  <application>
    <id type="integer">123</id>
    <name>My Application</name>
    <overview-url>https://rpm.newrelic.com/accounts/1/applications/123</overview-url>
    <servers-url>https://api.newrelic.com/api/v1/accounts/1/applications/123/servers</servers-url>
  </application>
  <application>
    <id type="integer">124</id>
    <name>My Application2</name>
    <overview-url>https://rpm.newrelic.com/accounts/1/applications/124</overview-url>
    <servers-url>https://api.newrelic.com/api/v1/accounts/1/applications/123/servers</servers-url>
  </application>
</applications>
"""