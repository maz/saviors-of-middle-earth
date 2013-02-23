require 'yaml'

@inputs=YAML.load_file(File.join(File.dirname(__FILE__),'assets','fixtures','fixture-inputs.yaml'))
def keys_to_symbols(x)
  x.keys.clone.each do |key|
    x[key.to_sym]=x[key]
    x.delete key
  end
  x.values.each do |val|
    if val.kind_of?(Hash)
      keys_to_symbols val
    elsif val.kind_of?(Array)
      val.each{|x| keys_to_symbols(x) if x.kind_of?(Hash) }
    end
  end
end
keys_to_symbols @inputs

@products=[]
@inputs[:classes].each do |cls|
  @inputs[:per_class].each do |itm|
    itm=itm.clone#SHALLOW copy
    itm[:name]="#{cls} #{itm[:name]}"
    itm[:description]=itm[:description].gsub("$CLASS",cls)
    @products<<itm
  end
end

@users={}
@random=Random.new(@inputs[:seed])

def rtween(min,max)
  @random.rand(max-min)+min
end

@inputs[:names].each do |name|
  break if @products.length==0
  @users[name]=[]
  rtween(@inputs[:min_products],@inputs[:max_products]).times do
    break unless @products.length>0
    idx=rtween(0,@products.length)
    @users[name]<<@products[idx]
    @products.delete_at idx
  end
end

#dump any remaining products on the last user
@users[@inputs[:names].last]+=@products if @products.length>0

File.open(File.join(File.dirname(__FILE__),'fixtures.yaml'),'w') do |f|
  f<<@users.to_yaml
end