import os

def create_test_plan(user_count, loop_count, base_url, path, ramp_time=5, output_file="dynamic_test_plan.jmx"):
    # JMeter test plan template
    test_plan_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.3">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="Test Plan">
      <elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="User Defined Variables">
        <collectionProp name="Arguments.arguments"/>
      </elementProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
    </TestPlan>
    <hashTree>
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Thread Group">
    <intProp name="ThreadGroup.num_threads">{user_count}</intProp>
    <intProp name="ThreadGroup.ramp_time">{ramp_time}</intProp>
        <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
        <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="Loop Controller">
    <stringProp name="LoopController.loops">{loop_count}</stringProp>
          <boolProp name="LoopController.continue_forever">false</boolProp>
        </elementProp>
      </ThreadGroup>
      <hashTree>
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="HTTP Request">
          <stringProp name="HTTPSampler.domain">{base_url}</stringProp>
          <stringProp name="HTTPSampler.path">{path}</stringProp>
          <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
          <stringProp name="HTTPSampler.method">GET</stringProp>
          <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
          <boolProp name="HTTPSampler.postBodyRaw">false</boolProp>
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables">
            <collectionProp name="Arguments.arguments"/>
          </elementProp>
        </HTTPSamplerProxy>
        <hashTree/>
        <ResultCollector guiclass="ViewResultsFullVisualizer" testclass="ResultCollector" testname="View Results Tree">
          <boolProp name="ResultCollector.error_logging">false</boolProp>
          <objProp>
            <name>saveConfig</name>
            <value class="SampleSaveConfiguration">
              <time>true</time>
              <latency>true</latency>
              <timestamp>true</timestamp>
              <success>true</success>
              <label>true</label>
              <code>true</code>
              <message>true</message>
              <threadName>true</threadName>
              <dataType>true</dataType>
              <encoding>false</encoding>
              <assertions>true</assertions>
              <subresults>true</subresults>
              <responseData>false</responseData>
              <samplerData>false</samplerData>
              <xml>false</xml>
              <fieldNames>true</fieldNames>
              <responseHeaders>false</responseHeaders>
              <requestHeaders>false</requestHeaders>
              <responseDataOnError>false</responseDataOnError>
              <saveAssertionResultsFailureMessage>true</saveAssertionResultsFailureMessage>
              <assertionsResultsToSave>0</assertionsResultsToSave>
              <bytes>true</bytes>
              <sentBytes>true</sentBytes>
              <url>true</url>
              <threadCounts>true</threadCounts>
              <idleTime>true</idleTime>
              <connectTime>true</connectTime>
            </value>
          </objProp>
          <stringProp name="filename">results.csv</stringProp>
        </ResultCollector>
        <hashTree/>
      </hashTree>
    </hashTree>
  </hashTree>
</jmeterTestPlan>"""

    # Save to file
    output_path = os.path.join(os.path.dirname(__file__), "../inputs", output_file)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(test_plan_template)
    print(f"Test plan saved to {output_path}")
    print(f"user_count: {user_count}, loop_count: {loop_count}, base_url: {base_url}, path: {path}")

import xml.etree.ElementTree as ET
import os

def update_jmx(base_url, path, users, loop_count):
    """
    JMX dosyasını günceller.
    Kullanıcıdan alınan base_url, path, users ve loop_count değerlerini dynamic_test_plan.jmx'e yazar.
    """
    
            
    inputs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'inputs')
    jmx_file_path = os.path.join(inputs_dir, "dynamic_test_plan.jmx")
    
    if not os.path.exists(jmx_file_path):
        raise FileNotFoundError(f"{jmx_file_path} bulunamadı. Lütfen doğru dosya yapısını kontrol edin.")

    tree = ET.parse(jmx_file_path)
    root = tree.getroot()
    
    


    # HTTPSamplerProxy düğümünü bul
    for elem in root.iter("HTTPSamplerProxy"):
        # Domain (base_url) ve Path güncelleme
        for prop in elem.findall("stringProp"):
            if prop.attrib["name"] == "HTTPSampler.domain":
                prop.text = base_url
            elif prop.attrib["name"] == "HTTPSampler.path":
                prop.text = path

    # ThreadGroup düğümünü bul ve kullanıcı sayısını güncelle
    for thread_group in root.iter("ThreadGroup"):
        for prop in thread_group.findall("intProp"):
            if prop.attrib["name"] == "ThreadGroup.num_threads":
                prop.text = str(users)
            elif prop.attrib["name"] == "LoopController.loops":
                prop.text = str(loop_count)

    # Güncellenmiş JMX dosyasını kaydet
    tree.write(jmx_file_path, encoding="UTF-8", xml_declaration=True)
    print(f"JMX dosyası başarıyla güncellendi: {jmx_file_path}")
