
RenderChannelColor vrayRE_Atmospheric_Effects {
  name="atmosphere";
  alias=100;
  color_mapping=1;
}

RenderChannelColor vrayRE_Diffuse {
  name="diffuse";
  alias=101;
}

RenderChannelColor vrayRE_Reflection {
  name="reflect";
  alias=102;
  color_mapping=1;
}

RenderChannelColor vrayRE_Refraction {
  name="refract";
  alias=103;
  color_mapping=1;
}

RenderChannelColor vrayRE_Self_Illumination {
  name="selfIllum";
  alias=104;
  color_mapping=1;
}

RenderChannelColor vrayRE_Shadow {
  name="shadow";
  alias=105;
  color_mapping=1;
}

RenderChannelColor vrayRE_Specular {
  name="specular";
  alias=106;
  color_mapping=1;
}

RenderChannelColor vrayRE_Lighting {
  name="lighting";
  alias=107;
  color_mapping=1;
}

RenderChannelColor vrayRE_GI {
  name="GI";
  alias=108;
  color_mapping=1;
}

RenderChannelColor vrayRE_Caustics {
  name="caustics";
  alias=109;
  color_mapping=1;
}

RenderChannelColor vrayRE_Raw_GI {
  name="rawGI";
  alias=110;
  color_mapping=1;
}

RenderChannelColor vrayRE_Raw_Light {
  name="rawLight";
  alias=111;
  color_mapping=1;
}

RenderChannelColor vrayRE_Raw_Shadow {
  name="rawShadow";
  alias=112;
  color_mapping=1;
}



RenderChannelColor vrayRE_Material_ID {
  name="materialID";
  alias=115;
  consider_for_aa=0;
  filtering=1;
}




RenderChannelColor vrayRE_Reflection_Filter {
  name="reflectionFilter";
  alias=118;
}

RenderChannelColor vrayRE_Raw_Reflection {
  name="rawReflection";
  alias=119;
  color_mapping=1;
}

RenderChannelColor vrayRE_Refraction_Filter {
  name="refractionFilter";
  alias=120;
}

RenderChannelColor vrayRE_Raw_Refraction {
  name="rawRefraction";
  alias=121;
  color_mapping=1;
}




RenderChannelColor vrayRE_Background {
  name="background";
  alias=124;
  color_mapping=1;
}



RenderChannelColor vrayRE_Matte_shadow {
  name="matteShadow";
  alias=128;
  consider_for_aa=0;
}

RenderChannelColor vrayRE_Total_Light {
  name="totalLight";
  alias=129;
  color_mapping=1;
}

RenderChannelColor vrayRE_Raw_Total_Light {
  name="rawTotalLight";
  alias=130;
  color_mapping=1;
}

RenderChannelColor vrayRE_Sample_Rate {
  name="sampleRate";
  alias=132;
  color_mapping=0;
}

RenderChannelColor vrayRE_SSS {
  name="SSS";
  alias=133;
  color_mapping=1;
}



RenderChannelGlossiness vrayRE_Reflection_glossiness {
  name="reflGloss";
  alias=135;
}

RenderChannelGlossiness vrayRE_Reflection_hilight_glossiness {
  name="reflHilightGloss";
  alias=136;
}

RenderChannelGlossiness vrayRE_Refraction_glossiness {
  name="refrGloss";
  alias=137;
}




RenderChannelColor vrayRE_Custom_Color {
  name="custom_color";
  alias=2000;
  color_mapping=1;
  filtering=1;
}





RenderChannelColor vrayRE_Material_Select {
  name="materialSelect";
  color_mapping=1;
}


RenderChannelColor vrayRE_Light_Select {
  name="lightselect";
  color_mapping=1;
  consider_for_aa=0;
}


