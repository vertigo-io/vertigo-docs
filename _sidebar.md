<hr/>
	<h3 class="q-version-select">
	Vertigo  
	<select id="versions" onchange="javascript:location.href=this.value+location.hash">
    <option value="/vertigo-docs/">v2.0.0 (current)</option>
    <!-- <option value="/vertigo-docs/v2.0.0/">v2.0.0</option> -->
  </select>
  <script>
	$( document ).ready({
		var $select = $('#versions');
		  $.ajax({
			url: 'https://api.github.com/repos/vertigo-io/vertigo-docs/tags',
		  }).then(function(options) {
			var i = 0;
			options.map(function(option) {
			  var $option = $('<option>');
			
			  $option
				.val('/vertigo-docs/'+(i>0)?option['name']:'')
				.text(option['name']+(i>0)?'':' (current)');          
			  $select.append($option);
			  i++;
			});
			var extractFromLocation = window.location.href.substring(window.location.origin.length,window.location.href.indexOf('/#/')+1);
			if(extractFromLocation.includes('draft')) {
			  $select.append('<option selected value="/vertigo-docs/draft/">draft</option>');
			}
			$select.val(extractFromLocation);			
		  });
		});
	});
  </script>
	</h3>
<hr/>

- Overview
  - [Introduction](overview/introduction.md)
  - [Philosophie](overview/philosophie.md)
  - [Références](overview/references.md)
  - [Ecosystème](overview/ecosystem.md)
  - [Modules](overview/modules.md)
- Getting-started
  - [Prérequis](getting-started/requirements.md)  
  - [Comment démarrer le moteur...](getting-started/helloworld.md)
  - [Real world Hello World !](getting-started/realworld_helloworld.md)  
- Basique
  - [Concepts](basic/concepts.md)
  - [Configuration](basic/configuration.md)
  - [Composants](basic/composants.md)
  - [MDA](basic/mda.md)
  - [Accès aux données](basic/dao.md)
  - [Recherche](basic/recherche.md)
  - [Sécurité](basic/securite.md)
  - [WebServices](basic/webservices.md)
  - [UI](basic/ui.md)
  - [Analytics](basic/analytics.md)
- Details des Modules
  - [Vega](advanced/vega.md)
  - [Account](advanced/account.md)
- Extensions
  - [UI](extensions/ui.md)
  - [Orchestra](extensions/orchestra.md)
  - [Quarto](extensions/quarto.md)
- [Changelog](changes.md)