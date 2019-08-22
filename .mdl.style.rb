all

rule 'MD013', :line_length => 119, :code_blocks => false
rule 'MD029', :style => "ordered"

exclude_rule 'MD004' # try to use * where possible but this is annoying in embedded blocks
exclude_rule 'MD005' # doesn't like 2 spaces on nested un-ordered lists
exclude_rule 'MD007' # doesn't like 4 spaced on unordered list within ordered list (but required if you want to render correctly)
