"""Se ejecuta en el contexto del verificador; usa su sesión de navegador."""
matrix=[]
value('action','ninguna');value('search','');value('state','')
years=c.evaluate('[...document.getElementById("map-year").options].map(o=>o.value)')
methods=c.evaluate('[...document.getElementById("method").options].map(o=>o.value)')
for year in years:
    value('map-year',year,'change')
    assert c.evaluate('window.Umbral6.state.year')==int(year)
    assert c.evaluate('document.getElementById("method").disabled')==(year!='2027')
    assert c.evaluate('document.getElementById("modulo-3").hidden')==(year!='2027')
    if year=='2027':
        for method in methods:
            value('method',method)
            assert c.evaluate('window.Umbral6.state.method')==method
            matrix.append({'year':year,'method':method})
    else:
        for state_key in ['','23','09']:
            value('state',state_key)
            assert c.evaluate('window.Umbral6.state.state')==state_key
            matrix.append({'year':year,'state':state_key})
    value('state','')
    screenshot('auditoria_ano_'+year+'.png','#paso-1-map')
value('map-year','2027','change');value('method','hgb')
states=c.evaluate('[...document.getElementById("state").options].map(o=>o.value).filter(Boolean)')
for state_key in states:
    value('search','');value('state',state_key)
    assert c.evaluate('window.Umbral6.state.state')==state_key
    assert c.evaluate('document.getElementById("d6-state-plan-content").textContent.trim().length')>50
value('state','23');value('search','23008')
for id in ['lens','min-confidence','distribution']:
    for option in c.evaluate(f'[...document.getElementById({json.dumps(id)}).options].map(o=>o.value)'):
        value(id,option)
        assert not c.errors,(id,option,c.errors)
for method in methods:
    value('method',method)
    for checked in [True,False]:
        c.evaluate('document.getElementById("stable").checked='+json.dumps(checked)+';document.getElementById("stable").dispatchEvent(new Event("input"))')
        assert not c.errors,(method,checked,c.errors)
value('method','hgb');value('min-confidence','todas')
actions=c.evaluate('[...document.getElementById("action").options].map(o=>o.value)')
for action in actions:
    value('action',action);value('reach','1000')
    if action=='personalizada':
        for response in ['0','50','100']:value('response',response)
    for mode in ['base','intervencion','cambio']:
        value('map-mode',mode)
        assert not c.errors,(action,mode,c.errors)
    assert c.evaluate('!document.getElementById("simulation-results").hidden')==(action!='ninguna')
value('action','sms_suecia');value('reach','1000');value('map-mode','base')
for scope in ['pais','estado','municipio']:
    value('simulation-scope',scope,'change')
    assert c.evaluate('document.getElementById("simulation-scope").value')==scope
    assert not c.errors,(scope,c.errors)
value('simulation-state','23','change');value('simulation-municipality','23008','change')
viewports=[]
for width in [1440,768,390,360]:
    c.call('Emulation.setDeviceMetricsOverride',{'width':width,'height':900 if width>768 else 844,'deviceScaleFactor':1,'mobile':width<768})
    c.call('Emulation.setTouchEmulationEnabled',{'enabled':width<768})
    c.evaluate('window.dispatchEvent(new Event("resize"))')
    time.sleep(.3)
    overflow=c.evaluate('({viewport:innerWidth,body:document.body.scrollWidth,root:document.documentElement.scrollWidth})')
    viewports.append(overflow)
    assert max(overflow['body'],overflow['root'])<=overflow['viewport']+2,('Desbordamiento horizontal',overflow)
    for section in ['inicio','modulo-1','modulo-2','modulo-3','evidencia']:
        c.evaluate(f'document.getElementById({json.dumps(section)}).scrollIntoView({{block:"start",behavior:"instant"}})')
        time.sleep(.12)
        screenshot('auditoria_'+str(width)+'_'+section+'.png')
        if section.startswith('modulo-'):
            geometry=c.evaluate(f'(()=>{{const h=document.querySelector(".d7-context-bar").getBoundingClientRect(),t=document.querySelector("#{section} .module-heading").getBoundingClientRect();return {{headerBottom:h.bottom,titleTop:t.top}}}})()')
            assert geometry['titleTop']>=geometry['headerBottom']-2,('Título oculto',width,section,geometry)
    # Controls must remain inside their container rather than overlap the next block.
    controls=c.evaluate('([...document.querySelectorAll("#paso-1 input:not([hidden]),#paso-1 select:not([hidden]),#simulation-inputs input:not([hidden]),#simulation-inputs select:not([hidden])")].filter(e=>e.getClientRects().length).map(e=>({id:e.id,left:e.getBoundingClientRect().left,right:e.getBoundingClientRect().right})))')
    assert all(x['left']>=-1 and x['right']<=width+1 for x in controls),('Control fuera de pantalla',width,controls)
    if width<768:
        c.evaluate('window.Umbral6.returnToMexico()')
        assert c.evaluate('document.querySelectorAll("#paso-1-map .legend small").length')==4
        screenshot('auditoria_'+str(width)+'_nacional.png','#paso-1-map')
        c.evaluate('window.Umbral6.selectMunicipality("23008")')
    assert not c.errors,c.errors
checks['complete_walkthrough']={'years':years,'methods':methods,'temporal_matrix':matrix,'states':len(states),'actions':actions,'viewports':viewports,'all_page_sections_captured':True,'page_errors':c.errors}
print('Recorrido ampliado:',len(years),'años,',len(methods),'métodos,',len(states),'estados,',len(actions),'acciones y 4 tamaños de pantalla.',flush=True)
