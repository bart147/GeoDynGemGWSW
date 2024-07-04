<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis simplifyAlgorithm="0" simplifyDrawingHints="0" version="3.16.16-Hannover" styleCategories="AllStyleCategories" hasScaleBasedVisibilityFlag="0" minScale="100000000" simplifyMaxScale="1" maxScale="0" simplifyDrawingTol="1" simplifyLocal="1" readOnly="0" labelsEnabled="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <temporal endField="" endExpression="" startExpression="" mode="0" enabled="0" durationField="" accumulate="0" startField="" durationUnit="min" fixedDuration="0">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <renderer-v2 enableorderby="0" symbollevels="0" type="RuleRenderer" forceraster="0">
    <rules key="{c3628ef9-e7aa-402e-844d-b6698b9af1c0}">
      <rule label="Geen Berging Knopen" filter="ELSE" key="{650ea6ae-827f-497d-b561-a49aa537ba25}" symbol="0"/>
      <rule label="Wel Berging Knopen" filter="&quot;B_M3_KNP&quot; >= 0" key="{bccf4deb-323f-4690-a2f1-fbe3dda8f8a7}" symbol="1"/>
    </rules>
    <symbols>
      <symbol force_rhr="0" alpha="1" clip_to_extent="1" type="marker" name="0">
        <layer class="SimpleMarker" locked="0" pass="0" enabled="1">
          <prop k="angle" v="0"/>
          <prop k="color" v="227,26,28,255"/>
          <prop k="horizontal_anchor_point" v="1"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="name" v="circle"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="35,35,35,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0"/>
          <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="scale_method" v="diameter"/>
          <prop k="size" v="2"/>
          <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="size_unit" v="MM"/>
          <prop k="vertical_anchor_point" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" alpha="1" clip_to_extent="1" type="marker" name="1">
        <layer class="SimpleMarker" locked="0" pass="0" enabled="1">
          <prop k="angle" v="0"/>
          <prop k="color" v="51,160,44,255"/>
          <prop k="horizontal_anchor_point" v="1"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="name" v="circle"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="35,35,35,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0"/>
          <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="scale_method" v="diameter"/>
          <prop k="size" v="2"/>
          <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="size_unit" v="MM"/>
          <prop k="vertical_anchor_point" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
  <customproperties>
    <property value="false" key="OnConvertFormatRegeneratePrimaryKey"/>
    <property value="0" key="embeddedWidgets/count"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer diagramType="Histogram" attributeLegend="1">
    <DiagramCategory width="15" penColor="#000000" penWidth="0" sizeScale="3x:0,0,0,0,0,0" spacing="5" direction="0" penAlpha="255" labelPlacementMethod="XHeight" showAxis="1" lineSizeType="MM" spacingUnitScale="3x:0,0,0,0,0,0" rotationOffset="270" sizeType="MM" spacingUnit="MM" lineSizeScale="3x:0,0,0,0,0,0" minimumSize="0" backgroundAlpha="255" scaleDependency="Area" diagramOrientation="Up" opacity="1" barWidth="5" minScaleDenominator="0" backgroundColor="#ffffff" height="15" scaleBasedVisibility="0" maxScaleDenominator="1e+08" enabled="0">
      <fontProperties style="" description="MS Shell Dlg 2,8.25,-1,5,50,0,0,0,0,0"/>
      <axisSymbol>
        <symbol force_rhr="0" alpha="1" clip_to_extent="1" type="line" name="">
          <layer class="SimpleLine" locked="0" pass="0" enabled="1">
            <prop k="align_dash_pattern" v="0"/>
            <prop k="capstyle" v="square"/>
            <prop k="customdash" v="5;2"/>
            <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <prop k="customdash_unit" v="MM"/>
            <prop k="dash_pattern_offset" v="0"/>
            <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <prop k="dash_pattern_offset_unit" v="MM"/>
            <prop k="draw_inside_polygon" v="0"/>
            <prop k="joinstyle" v="bevel"/>
            <prop k="line_color" v="35,35,35,255"/>
            <prop k="line_style" v="solid"/>
            <prop k="line_width" v="0.26"/>
            <prop k="line_width_unit" v="MM"/>
            <prop k="offset" v="0"/>
            <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <prop k="offset_unit" v="MM"/>
            <prop k="ring_filter" v="0"/>
            <prop k="tweak_dash_pattern_on_corners" v="0"/>
            <prop k="use_custom_dash" v="0"/>
            <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
          </layer>
        </symbol>
      </axisSymbol>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings dist="0" priority="0" showAll="1" obstacle="0" placement="0" zIndex="0" linePlacementFlags="18">
    <properties>
      <Option type="Map">
        <Option value="" type="QString" name="name"/>
        <Option name="properties"/>
        <Option value="collection" type="QString" name="type"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions geometryPrecision="0" removeDuplicateNodes="0">
    <activeChecks/>
    <checkConfiguration/>
  </geometryOptions>
  <legend type="default-vector"/>
  <referencedLayers/>
  <fieldConfiguration>
    <field configurationFlags="None" name="geo_id">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="Stelsel">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="naam">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="type">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="Maaiveldhoogte">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="Maaiveldschematisering">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="MateriaalPut">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="VormPut">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="BreedtePut">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="LengtePut">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="HoogtePut">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="US_geo_id">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="US_Stelsel">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="US_naam">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="US_type">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="US_beginpunt">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="US_MateriaalLeiding">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="US_VormLeiding">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="US_BreedteLeiding">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="US_HoogteLeiding">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="US_LengteLeiding">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="US_BobBeginpuntLeiding">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="DS_geo_id">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="DS_Stelsel">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="DS_naam">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="DS_type">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="DS_eindpunt">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="DS_MateriaalLeiding">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="DS_VormLeiding">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="DS_BreedteLeiding">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="DS_HoogteLeiding">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="DS_BobEindpuntLeiding">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="BEM_ID">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="BEM_ID_SP">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="Maaiveldhoogte_q1">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="Drempelniveau_min">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="OVH_D">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="B_M3_KNP">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias field="geo_id" index="0" name=""/>
    <alias field="Stelsel" index="1" name=""/>
    <alias field="naam" index="2" name=""/>
    <alias field="type" index="3" name=""/>
    <alias field="Maaiveldhoogte" index="4" name=""/>
    <alias field="Maaiveldschematisering" index="5" name=""/>
    <alias field="MateriaalPut" index="6" name=""/>
    <alias field="VormPut" index="7" name=""/>
    <alias field="BreedtePut" index="8" name=""/>
    <alias field="LengtePut" index="9" name=""/>
    <alias field="HoogtePut" index="10" name=""/>
    <alias field="US_geo_id" index="11" name=""/>
    <alias field="US_Stelsel" index="12" name=""/>
    <alias field="US_naam" index="13" name=""/>
    <alias field="US_type" index="14" name=""/>
    <alias field="US_beginpunt" index="15" name=""/>
    <alias field="US_MateriaalLeiding" index="16" name=""/>
    <alias field="US_VormLeiding" index="17" name=""/>
    <alias field="US_BreedteLeiding" index="18" name=""/>
    <alias field="US_HoogteLeiding" index="19" name=""/>
    <alias field="US_LengteLeiding" index="20" name=""/>
    <alias field="US_BobBeginpuntLeiding" index="21" name=""/>
    <alias field="DS_geo_id" index="22" name=""/>
    <alias field="DS_Stelsel" index="23" name=""/>
    <alias field="DS_naam" index="24" name=""/>
    <alias field="DS_type" index="25" name=""/>
    <alias field="DS_eindpunt" index="26" name=""/>
    <alias field="DS_MateriaalLeiding" index="27" name=""/>
    <alias field="DS_VormLeiding" index="28" name=""/>
    <alias field="DS_BreedteLeiding" index="29" name=""/>
    <alias field="DS_HoogteLeiding" index="30" name=""/>
    <alias field="DS_BobEindpuntLeiding" index="31" name=""/>
    <alias field="BEM_ID" index="32" name=""/>
    <alias field="BEM_ID_SP" index="33" name=""/>
    <alias field="Maaiveldhoogte_q1" index="34" name=""/>
    <alias field="Drempelniveau_min" index="35" name=""/>
    <alias field="OVH_D" index="36" name=""/>
    <alias field="B_M3_KNP" index="37" name=""/>
  </aliases>
  <defaults>
    <default field="geo_id" expression="" applyOnUpdate="0"/>
    <default field="Stelsel" expression="" applyOnUpdate="0"/>
    <default field="naam" expression="" applyOnUpdate="0"/>
    <default field="type" expression="" applyOnUpdate="0"/>
    <default field="Maaiveldhoogte" expression="" applyOnUpdate="0"/>
    <default field="Maaiveldschematisering" expression="" applyOnUpdate="0"/>
    <default field="MateriaalPut" expression="" applyOnUpdate="0"/>
    <default field="VormPut" expression="" applyOnUpdate="0"/>
    <default field="BreedtePut" expression="" applyOnUpdate="0"/>
    <default field="LengtePut" expression="" applyOnUpdate="0"/>
    <default field="HoogtePut" expression="" applyOnUpdate="0"/>
    <default field="US_geo_id" expression="" applyOnUpdate="0"/>
    <default field="US_Stelsel" expression="" applyOnUpdate="0"/>
    <default field="US_naam" expression="" applyOnUpdate="0"/>
    <default field="US_type" expression="" applyOnUpdate="0"/>
    <default field="US_beginpunt" expression="" applyOnUpdate="0"/>
    <default field="US_MateriaalLeiding" expression="" applyOnUpdate="0"/>
    <default field="US_VormLeiding" expression="" applyOnUpdate="0"/>
    <default field="US_BreedteLeiding" expression="" applyOnUpdate="0"/>
    <default field="US_HoogteLeiding" expression="" applyOnUpdate="0"/>
    <default field="US_LengteLeiding" expression="" applyOnUpdate="0"/>
    <default field="US_BobBeginpuntLeiding" expression="" applyOnUpdate="0"/>
    <default field="DS_geo_id" expression="" applyOnUpdate="0"/>
    <default field="DS_Stelsel" expression="" applyOnUpdate="0"/>
    <default field="DS_naam" expression="" applyOnUpdate="0"/>
    <default field="DS_type" expression="" applyOnUpdate="0"/>
    <default field="DS_eindpunt" expression="" applyOnUpdate="0"/>
    <default field="DS_MateriaalLeiding" expression="" applyOnUpdate="0"/>
    <default field="DS_VormLeiding" expression="" applyOnUpdate="0"/>
    <default field="DS_BreedteLeiding" expression="" applyOnUpdate="0"/>
    <default field="DS_HoogteLeiding" expression="" applyOnUpdate="0"/>
    <default field="DS_BobEindpuntLeiding" expression="" applyOnUpdate="0"/>
    <default field="BEM_ID" expression="" applyOnUpdate="0"/>
    <default field="BEM_ID_SP" expression="" applyOnUpdate="0"/>
    <default field="Maaiveldhoogte_q1" expression="" applyOnUpdate="0"/>
    <default field="Drempelniveau_min" expression="" applyOnUpdate="0"/>
    <default field="OVH_D" expression="" applyOnUpdate="0"/>
    <default field="B_M3_KNP" expression="" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint field="geo_id" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="Stelsel" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="naam" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="type" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="Maaiveldhoogte" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="Maaiveldschematisering" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="MateriaalPut" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="VormPut" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="BreedtePut" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="LengtePut" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="HoogtePut" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="US_geo_id" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="US_Stelsel" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="US_naam" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="US_type" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="US_beginpunt" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="US_MateriaalLeiding" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="US_VormLeiding" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="US_BreedteLeiding" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="US_HoogteLeiding" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="US_LengteLeiding" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="US_BobBeginpuntLeiding" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="DS_geo_id" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="DS_Stelsel" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="DS_naam" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="DS_type" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="DS_eindpunt" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="DS_MateriaalLeiding" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="DS_VormLeiding" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="DS_BreedteLeiding" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="DS_HoogteLeiding" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="DS_BobEindpuntLeiding" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="BEM_ID" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="BEM_ID_SP" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="Maaiveldhoogte_q1" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="Drempelniveau_min" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="OVH_D" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
    <constraint field="B_M3_KNP" notnull_strength="0" constraints="0" exp_strength="0" unique_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="geo_id" exp="" desc=""/>
    <constraint field="Stelsel" exp="" desc=""/>
    <constraint field="naam" exp="" desc=""/>
    <constraint field="type" exp="" desc=""/>
    <constraint field="Maaiveldhoogte" exp="" desc=""/>
    <constraint field="Maaiveldschematisering" exp="" desc=""/>
    <constraint field="MateriaalPut" exp="" desc=""/>
    <constraint field="VormPut" exp="" desc=""/>
    <constraint field="BreedtePut" exp="" desc=""/>
    <constraint field="LengtePut" exp="" desc=""/>
    <constraint field="HoogtePut" exp="" desc=""/>
    <constraint field="US_geo_id" exp="" desc=""/>
    <constraint field="US_Stelsel" exp="" desc=""/>
    <constraint field="US_naam" exp="" desc=""/>
    <constraint field="US_type" exp="" desc=""/>
    <constraint field="US_beginpunt" exp="" desc=""/>
    <constraint field="US_MateriaalLeiding" exp="" desc=""/>
    <constraint field="US_VormLeiding" exp="" desc=""/>
    <constraint field="US_BreedteLeiding" exp="" desc=""/>
    <constraint field="US_HoogteLeiding" exp="" desc=""/>
    <constraint field="US_LengteLeiding" exp="" desc=""/>
    <constraint field="US_BobBeginpuntLeiding" exp="" desc=""/>
    <constraint field="DS_geo_id" exp="" desc=""/>
    <constraint field="DS_Stelsel" exp="" desc=""/>
    <constraint field="DS_naam" exp="" desc=""/>
    <constraint field="DS_type" exp="" desc=""/>
    <constraint field="DS_eindpunt" exp="" desc=""/>
    <constraint field="DS_MateriaalLeiding" exp="" desc=""/>
    <constraint field="DS_VormLeiding" exp="" desc=""/>
    <constraint field="DS_BreedteLeiding" exp="" desc=""/>
    <constraint field="DS_HoogteLeiding" exp="" desc=""/>
    <constraint field="DS_BobEindpuntLeiding" exp="" desc=""/>
    <constraint field="BEM_ID" exp="" desc=""/>
    <constraint field="BEM_ID_SP" exp="" desc=""/>
    <constraint field="Maaiveldhoogte_q1" exp="" desc=""/>
    <constraint field="Drempelniveau_min" exp="" desc=""/>
    <constraint field="OVH_D" exp="" desc=""/>
    <constraint field="B_M3_KNP" exp="" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig actionWidgetStyle="dropDown" sortExpression="&quot;geo_id&quot;" sortOrder="0">
    <columns>
      <column width="-1" hidden="0" type="field" name="geo_id"/>
      <column width="-1" hidden="0" type="field" name="Stelsel"/>
      <column width="-1" hidden="0" type="field" name="naam"/>
      <column width="-1" hidden="0" type="field" name="type"/>
      <column width="-1" hidden="0" type="field" name="Maaiveldhoogte"/>
      <column width="-1" hidden="0" type="field" name="Maaiveldschematisering"/>
      <column width="-1" hidden="0" type="field" name="MateriaalPut"/>
      <column width="-1" hidden="0" type="field" name="VormPut"/>
      <column width="-1" hidden="0" type="field" name="BreedtePut"/>
      <column width="-1" hidden="0" type="field" name="LengtePut"/>
      <column width="-1" hidden="0" type="field" name="HoogtePut"/>
      <column width="-1" hidden="0" type="field" name="US_geo_id"/>
      <column width="-1" hidden="0" type="field" name="US_Stelsel"/>
      <column width="-1" hidden="0" type="field" name="US_naam"/>
      <column width="-1" hidden="0" type="field" name="US_type"/>
      <column width="-1" hidden="0" type="field" name="US_beginpunt"/>
      <column width="-1" hidden="0" type="field" name="US_MateriaalLeiding"/>
      <column width="-1" hidden="0" type="field" name="US_VormLeiding"/>
      <column width="-1" hidden="0" type="field" name="US_BreedteLeiding"/>
      <column width="-1" hidden="0" type="field" name="US_HoogteLeiding"/>
      <column width="-1" hidden="0" type="field" name="US_LengteLeiding"/>
      <column width="-1" hidden="0" type="field" name="US_BobBeginpuntLeiding"/>
      <column width="-1" hidden="0" type="field" name="DS_geo_id"/>
      <column width="-1" hidden="0" type="field" name="DS_Stelsel"/>
      <column width="-1" hidden="0" type="field" name="DS_naam"/>
      <column width="-1" hidden="0" type="field" name="DS_type"/>
      <column width="-1" hidden="0" type="field" name="DS_eindpunt"/>
      <column width="-1" hidden="0" type="field" name="DS_MateriaalLeiding"/>
      <column width="-1" hidden="0" type="field" name="DS_VormLeiding"/>
      <column width="-1" hidden="0" type="field" name="DS_BreedteLeiding"/>
      <column width="-1" hidden="0" type="field" name="DS_HoogteLeiding"/>
      <column width="-1" hidden="0" type="field" name="DS_BobEindpuntLeiding"/>
      <column width="-1" hidden="0" type="field" name="BEM_ID"/>
      <column width="-1" hidden="0" type="field" name="BEM_ID_SP"/>
      <column width="-1" hidden="0" type="field" name="Maaiveldhoogte_q1"/>
      <column width="-1" hidden="0" type="field" name="Drempelniveau_min"/>
      <column width="-1" hidden="0" type="field" name="OVH_D"/>
      <column width="-1" hidden="0" type="field" name="B_M3_KNP"/>
      <column width="-1" hidden="1" type="actions"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1"></editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath></editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
QGIS forms can have a Python function that is called when the form is
opened.

Use this function to add extra logic to your forms.

Enter the name of the function in the "Python Init function"
field.
An example follows:
"""
from qgis.PyQt.QtWidgets import QWidget

def my_form_open(dialog, layer, feature):
	geom = feature.geometry()
	control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>generatedlayout</editorlayout>
  <editable>
    <field editable="1" name="BEM_ID"/>
    <field editable="1" name="BEM_ID_SP"/>
    <field editable="1" name="B_M3_KNP"/>
    <field editable="1" name="BreedtePut"/>
    <field editable="1" name="DS_BobEindpuntLeiding"/>
    <field editable="1" name="DS_BreedteLeiding"/>
    <field editable="1" name="DS_HoogteLeiding"/>
    <field editable="1" name="DS_MateriaalLeiding"/>
    <field editable="1" name="DS_Stelsel"/>
    <field editable="1" name="DS_VormLeiding"/>
    <field editable="1" name="DS_eindpunt"/>
    <field editable="1" name="DS_geo_id"/>
    <field editable="1" name="DS_naam"/>
    <field editable="1" name="DS_type"/>
    <field editable="1" name="Drempelniveau_min"/>
    <field editable="1" name="HoogtePut"/>
    <field editable="1" name="LengtePut"/>
    <field editable="1" name="Maaiveldhoogte"/>
    <field editable="1" name="Maaiveldhoogte_q1"/>
    <field editable="1" name="Maaiveldschematisering"/>
    <field editable="1" name="MateriaalPut"/>
    <field editable="1" name="OVH_D"/>
    <field editable="1" name="Stelsel"/>
    <field editable="1" name="US_BobBeginpuntLeiding"/>
    <field editable="1" name="US_BreedteLeiding"/>
    <field editable="1" name="US_HoogteLeiding"/>
    <field editable="1" name="US_LengteLeiding"/>
    <field editable="1" name="US_MateriaalLeiding"/>
    <field editable="1" name="US_Stelsel"/>
    <field editable="1" name="US_VormLeiding"/>
    <field editable="1" name="US_beginpunt"/>
    <field editable="1" name="US_geo_id"/>
    <field editable="1" name="US_naam"/>
    <field editable="1" name="US_type"/>
    <field editable="1" name="VormPut"/>
    <field editable="1" name="geo_id"/>
    <field editable="1" name="naam"/>
    <field editable="1" name="type"/>
  </editable>
  <labelOnTop>
    <field name="BEM_ID" labelOnTop="0"/>
    <field name="BEM_ID_SP" labelOnTop="0"/>
    <field name="B_M3_KNP" labelOnTop="0"/>
    <field name="BreedtePut" labelOnTop="0"/>
    <field name="DS_BobEindpuntLeiding" labelOnTop="0"/>
    <field name="DS_BreedteLeiding" labelOnTop="0"/>
    <field name="DS_HoogteLeiding" labelOnTop="0"/>
    <field name="DS_MateriaalLeiding" labelOnTop="0"/>
    <field name="DS_Stelsel" labelOnTop="0"/>
    <field name="DS_VormLeiding" labelOnTop="0"/>
    <field name="DS_eindpunt" labelOnTop="0"/>
    <field name="DS_geo_id" labelOnTop="0"/>
    <field name="DS_naam" labelOnTop="0"/>
    <field name="DS_type" labelOnTop="0"/>
    <field name="Drempelniveau_min" labelOnTop="0"/>
    <field name="HoogtePut" labelOnTop="0"/>
    <field name="LengtePut" labelOnTop="0"/>
    <field name="Maaiveldhoogte" labelOnTop="0"/>
    <field name="Maaiveldhoogte_q1" labelOnTop="0"/>
    <field name="Maaiveldschematisering" labelOnTop="0"/>
    <field name="MateriaalPut" labelOnTop="0"/>
    <field name="OVH_D" labelOnTop="0"/>
    <field name="Stelsel" labelOnTop="0"/>
    <field name="US_BobBeginpuntLeiding" labelOnTop="0"/>
    <field name="US_BreedteLeiding" labelOnTop="0"/>
    <field name="US_HoogteLeiding" labelOnTop="0"/>
    <field name="US_LengteLeiding" labelOnTop="0"/>
    <field name="US_MateriaalLeiding" labelOnTop="0"/>
    <field name="US_Stelsel" labelOnTop="0"/>
    <field name="US_VormLeiding" labelOnTop="0"/>
    <field name="US_beginpunt" labelOnTop="0"/>
    <field name="US_geo_id" labelOnTop="0"/>
    <field name="US_naam" labelOnTop="0"/>
    <field name="US_type" labelOnTop="0"/>
    <field name="VormPut" labelOnTop="0"/>
    <field name="geo_id" labelOnTop="0"/>
    <field name="naam" labelOnTop="0"/>
    <field name="type" labelOnTop="0"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"geo_id"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
